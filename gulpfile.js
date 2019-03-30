/// <binding ProjectOpened='watch' />

const gulp = require('gulp');
const sass = require('gulp-sass');
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS = require('gulp-clean-css');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');

const config = {
    sass: {
        sources: './wwwroot/css/main.scss',
        options: {
            precision: 10,
            outputStyle: 'expanded'
        },
        autoprefixerOptions: {
            browsers: ['> 1%', 'last 2 versions', 'Firefox ESR', 'Opera 12.1'],
            cascade: false
        }
    },
    css: {
        sources: [
            './wwwroot/css/reset.css',
            './wwwroot/css/pocketgrid.css',
            './wwwroot/css/main.css'
        ],
        options: {
            level: {
                1: {
                    specialComments: 0
                }
            }
        }
    },
    js: {
        sources: [
            './wwwroot/js/tinynav.js',
            './wwwroot/js/moment.js',
            './wwwroot/js/main.js'
        ]
    }
};

gulp.task('compile-sass', () =>
    gulp.src(config.sass.sources, { base: './' })
        .pipe(sass(config.sass.options).on('error', sass.logError))
        .pipe(autoprefixer(config.sass.autoprefixerOptions))
        .pipe(gulp.dest('.')));

gulp.task('bundle-and-minify-css', () =>
    gulp.src(config.css.sources)
        .pipe(concat('all.css'))
        .pipe(cleanCSS(config.css.options))
        .pipe(gulp.dest('./wwwroot/css')));

gulp.task('bundle-and-minify-js', () =>
    gulp.src(config.js.sources)
        .pipe(concat('all.js'))
        .pipe(uglify())
        .pipe(gulp.dest('./wwwroot/js')));

gulp.task('watch', () => {
    gulp.watch(config.sass.sources, gulp.series('compile-sass'));
    gulp.watch(config.css.sources, gulp.series('bundle-and-minify-css'));
    gulp.watch(config.js.sources, gulp.series('bundle-and-minify-js'));
});
