/**
 * Сбор UTM-меток на сайте для передачи в Битрикс24 (UTM_SOURCE, UTM_MEDIUM, ...).
 * Подробности: bitrix/docs/utm-tags-crm-funnel.md
 *
 * 1. Подключить на ВСЕХ страницах сайта.
 * 2. В формы добавить скрытые поля: <input type="hidden" name="UTM_SOURCE"> и т.д. —
 *    скрипт заполнит их сам. Либо вызвать window.getUtm() при отправке через fetch.
 */
(function () {
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  var DAYS = 30;

  // Запомнить метки из URL (если есть хотя бы одна — перезаписываем весь набор)
  var params = new URLSearchParams(location.search);
  if (KEYS.some(function (k) { return params.get(k); })) {
    KEYS.forEach(function (k) {
      document.cookie = k + '=' + encodeURIComponent(params.get(k) || '') +
        '; path=/; max-age=' + (DAYS * 86400) + '; SameSite=Lax';
    });
  }

  // { UTM_SOURCE: '...', UTM_MEDIUM: '...', ... } — ключи как поля CRM
  window.getUtm = function () {
    var out = {};
    document.cookie.split('; ').forEach(function (c) {
      var i = c.indexOf('=');
      var k = c.slice(0, i);
      if (KEYS.indexOf(k) !== -1) out[k.toUpperCase()] = decodeURIComponent(c.slice(i + 1));
    });
    return out;
  };

  // Заполнить скрытые поля во всех формах
  document.addEventListener('DOMContentLoaded', function () {
    var utm = window.getUtm();
    Object.keys(utm).forEach(function (name) {
      document.querySelectorAll('input[name="' + name + '"]').forEach(function (el) {
        el.value = utm[name];
      });
    });
  });
})();
