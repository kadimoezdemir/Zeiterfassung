from flask_assets import Bundle

common_css = Bundle(
    'main/css/vendor/bootstrap.css',
    'main/css/vendor/fontawesome-all.css',
    'main/css/main.css',
    filters='cssmin',
    output='public/css/common.css'
)

common_js = Bundle(
    'main/js/vendor/jquery.js',
    'main/js/vendor/popper.js',
    'main/js/vendor/bootstrap.js',
    Bundle(
        'main/js/main.js',
        filters='jsmin'
    ),
    output='public/js/common.js'
)