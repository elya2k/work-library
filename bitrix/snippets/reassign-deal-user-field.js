/*
 * Массовая замена сотрудника в пользовательском поле сделки (тип «Пользователь»),
 * например «Менеджер ОП»: старый (в т.ч. уволенный) → новый.
 *
 * Запуск: открыть свой Битрикс24 в браузере → F12 → Console → вставить скрипт целиком → Enter.
 * Сначала запускать с DRY_RUN = true (только посчитает), потом с false (заменит).
 * Вебхук после работы удалить. URL вебхука в репозиторий не коммитить.
 */
(async () => {
  const WEBHOOK = 'https://ВАШ-ПОРТАЛ.bitrix24.kz/rest/1/КЛЮЧ/'; // входящий вебхук с правами CRM
  const FIELD_LABEL = 'Менеджер ОП'; // название поля, как в карточке
  const OLD_USER_ID = 0;             // ID старого сотрудника (из ссылки на профиль: /user/123/)
  const NEW_USER_ID = 0;             // ID нового сотрудника
  const ONLY_OPEN = false;           // true — только незакрытые сделки
  const DRY_RUN = true;              // true — только показать, сколько сделок найдено

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const call = async (method, params) => {
    const res = await fetch(WEBHOOK + method + '.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    const data = await res.json();
    if (data.error) throw new Error(method + ': ' + data.error + ' ' + (data.error_description || ''));
    return data;
  };

  if (!OLD_USER_ID || !NEW_USER_ID) throw new Error('Заполните OLD_USER_ID и NEW_USER_ID');

  const fields = (await call('crm.deal.fields', {})).result;
  const code = Object.keys(fields).find((k) => {
    const f = fields[k];
    return k.startsWith('UF_CRM_') &&
      [f.formLabel, f.listLabel, f.filterLabel].some((l) => (l || '').trim() === FIELD_LABEL);
  });
  if (!code) throw new Error('Поле «' + FIELD_LABEL + '» не найдено. Проверьте название.');
  const field = fields[code];
  console.log('Поле:', code, 'тип:', field.type, 'множественное:', field.isMultiple);

  const deals = [];
  let lastId = 0;
  for (;;) {
    const filter = { [code]: OLD_USER_ID, '>ID': lastId };
    if (ONLY_OPEN) filter.CLOSED = 'N';
    const page = (await call('crm.deal.list', {
      filter, select: ['ID', code], order: { ID: 'ASC' }, start: -1,
    })).result;
    deals.push(...page);
    if (page.length < 50) break;
    lastId = page[page.length - 1].ID;
    await sleep(500);
  }
  console.log('Найдено сделок:', deals.length);
  if (DRY_RUN || !deals.length) {
    console.log(DRY_RUN ? 'DRY_RUN: ничего не изменено. Поставьте DRY_RUN = false и запустите снова.' : 'Менять нечего.');
    return;
  }

  const enc = encodeURIComponent;
  let ok = 0;
  const errors = [];
  for (let i = 0; i < deals.length; i += 50) {
    const cmd = {};
    for (const d of deals.slice(i, i + 50)) {
      let q = 'crm.deal.update?id=' + d.ID;
      if (field.isMultiple) {
        const vals = [].concat(d[code] || []).map(Number)
          .map((v) => (v === OLD_USER_ID ? NEW_USER_ID : v));
        [...new Set(vals)].forEach((v) => { q += '&' + enc('fields[' + code + '][]') + '=' + v; });
      } else {
        q += '&' + enc('fields[' + code + ']') + '=' + NEW_USER_ID;
      }
      cmd['d' + d.ID] = q;
    }
    const r = (await call('batch', { halt: 0, cmd })).result;
    ok += Object.keys(r.result || {}).length;
    for (const [k, e] of Object.entries(r.result_error || {})) {
      if (e && (!Array.isArray(e) || e.length)) errors.push(k + ': ' + JSON.stringify(e));
    }
    console.log('Обработано', Math.min(i + 50, deals.length), 'из', deals.length);
    await sleep(500);
  }
  console.log('Готово. Успешно:', ok, 'Ошибок:', errors.length);
  if (errors.length) console.log(errors.join('\n'));
})();
