(function ($) {
  var rc = {
    'common': {
      mode: 'debug',
      $window: $(window),
      breakpoint_xs: 768,
      breakpoint_sm: 992,
      breakpoint_md: 1280,

      init: function () {

        // Create your global vars here
        rc.common.$body = $(document.body);
        rc.common.$header = $('#header');

        // Vall your function here
        rc.common.welcomeSetup();
        rc.common.cancelPostSubmissionSetup();
        rc.common.socialSignInSetup();
      },
      // Create your function here
      welcomeSetup: function () {
        console.log('%cWelcome To Community Radio!', 'color: red; font-size: 12px; font-weight: bold');
      },
      socialSignInSetup: function () {
        const $socialFacebookItem = $('.facebook').find('img');
        const $socialGoogleItem = $('.google-plus').find('img');

        console.log($socialGoogleItem);

        $socialFacebookItem.attr('src', '../static/img/icons/facebook_icon.png');
        $socialGoogleItem.attr('src', '../static/img/icons/google_plus_icon.png');
      },
      cancelPostSubmissionSetup: function () {
        const $cancelBtn = $('#js--cancel-submission');

        $cancelBtn.on('click', () => {
          window.history.back();
        })
      }
    },
  };

  var UTIL = {
    fire: function (func, funcname, args) {
      var fire;
      var namespace = rc;
      funcname = (funcname === undefined) ? 'init' : funcname;
      fire = func !== '';
      fire = fire && namespace[func];
      fire = fire && typeof namespace[func][funcname] === 'function';

      if (fire) {
        namespace[func][funcname](args);
      }
    },
    loadEvents: function () {
      // Fire common init JS
      UTIL.fire('common');

      // Fire page-specific init JS, and then finalize JS
      $.each(document.body.className.replace(/-/g, '_').split(/\s+/), function (i, classnm) {
        UTIL.fire(classnm);
        UTIL.fire(classnm, 'finalize');
      });

      // Fire common finalize JS
      UTIL.fire('common', 'finalize');
    }
  };

  window.log = function () {
    log.history = log.history || [];   // store logs to an array for reference
    log.history.push(arguments);

    if (rc.common.mode === 'debug') {
      if (this.console) {
        console.log(Array.prototype.slice.call(arguments));
      }
    }
  };

  $(document).ready(UTIL.loadEvents);

})(jQuery);
