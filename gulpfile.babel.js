const gulp = require('gulp');
const bs = require('browser-sync');
const sass = require('gulp-sass');
const cssnano = require('gulp-cssnano');
const sourcemaps = require('gulp-sourcemaps');
const autoprefixer = require('gulp-autoprefixer');
const scsslint = require('gulp-scss-lint');

//-- path config
const stylesPath    = 'styles/**/*.scss';

// Sass Workflow
gulp.task('workflow', () => {
	return gulp.src(stylesPath)
    .pipe(scsslint())
		.pipe(sourcemaps.init())
		.pipe(sass().on('error', sass.logError))
		.pipe(autoprefixer({
			browsers: ['last 2 versions'],
			cascade: false
    }))
		.pipe(cssnano())
		.pipe(sourcemaps.write('./'))
		.pipe(rename({
			suffix: '.min'
		}))
	.pipe(gulp.dest('./styles/'))
  .pipe(bs.stream());
});

//-- Static server
gulp.task('dev', () => {
  bs.init({
    server: {
      baseDir: "./"
    },
    ghostMode: false
  });

  gulp.watch(stylesPath, ['workflow']).on('change', () => {
    bs.reload();
  });
  
});
