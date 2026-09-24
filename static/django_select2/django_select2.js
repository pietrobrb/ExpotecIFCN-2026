/* global define, jQuery */
(function (factory) {
  if (typeof define === 'function' && define.amd) {
    define(['jquery'], factory)
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('jquery'))
  } else {
    // Browser globals
    factory(jQuery || window.django.jQuery)
  }
}(function ($) {
  'use strict'
  var init = function ($element, options) {
    $element.select2(options)
  }

  var initHeavy = function ($element, options) {
    var settings = $.extend({
      ajax: {
        data: function (params) {
          var result = {
            term: params.term,
            page: params.page,
            field_id: $element.data('field_id')
          }

          var dependentFields = $element.data('select2-dependent-fields')
          if (dependentFields) {
            dependentFields = dependentFields.trim().split(/\s+/)
            $.each(dependentFields, function (i, dependentField) {
              // extract form prefix
              var prefix = "";
              var index = $element.attr("name").lastIndexOf("-");
              if (index > 0) {
                prefix = $element.attr("name").substr(0, index + 1);
              }
              // add form prefix on dependent field name
              var field = $(
                "[name=" + prefix + dependentField + "]",
                $element.closest("form")
              );
              // if not found try the old way
              if (!field.length) {
                field = $(
                  "[name=" + dependentField + "]",
                  $element.closest("form")
                );
              }
              result[dependentField] = field.val();
            })
          }

          return result
        },
        processResults: function (data, page) {
          return {
            results: data.results,
            pagination: {
              more: data.more
            }
          }
        }
      }
    }, options)

    $element.select2(settings)
  }

  $.fn.djangoSelect2 = function (options) {
    var settings = $.extend({}, options)
    $.each(this, function (i, element) {
      var $element = $(element)
      if ($element.hasClass('django-select2-heavy')) {
        initHeavy($element, settings)
      } else {
        init($element, settings)
      }
      $element.on('select2:select', function (e) {
        var name = $(e.currentTarget).attr('name')
        $('[data-select2-dependent-fields~=' + name + ']').each(function () {
          $(this).val('').trigger('change')
        })
      })
    })
    return this
  }

  $(function () {
    $('.django-select2').djangoSelect2()
  })

  return $.fn.djangoSelect2
}))
