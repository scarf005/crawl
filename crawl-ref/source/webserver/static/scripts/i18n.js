define([], function () {
    var catalog = window.webtiles_i18n || {};

    function tr(context, fallback)
    {
        return Object.prototype.hasOwnProperty.call(catalog, context)
            ? catalog[context]
            : fallback;
    }

    function trf(context, fallback, values)
    {
        return tr(context, fallback).replace(/\{([a-z_]+)\}/gi, function (match, key) {
            return Object.prototype.hasOwnProperty.call(values, key)
                ? values[key]
                : match;
        });
    }

    return {
        tr: tr,
        trf: trf,
    };
});
