const fs = require('fs');
const json = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const version = json.version;

var msg = "// jSmearHash Version " + version + "\n"
msg += "// Author: Piyush Raj" + "\n";
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

const gulp = require("gulp");
const concat = require('gulp-concat');
const beautify = require('gulp-jsbeautifier');
const composer = require('gulp-uglify/composer');
const uglify = require('uglify-es');
const minify = composer(uglify, console);
// const autoprefixer = require('gulp-autoprefixer')
// const sourcemaps = require('gulp-sourcemaps')
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




console.clear();
let files = "./*.js";



function buildDev() {
    return (
        gulp.src(files)
            .pipe(concat('jsmearhash.js'))
            .pipe(beautify())
            // .pipe(uglify())
            // .pipe(inject.prepend(msg))
            .on("error", function (e) {
                console.log(e.toString());
                this.emit("end");
            })
            .pipe(gulp.dest('./dist/'))
    )
}
gulp.task("buildDev", gulp.series(buildDev));
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


function buildMin() {
    return (
        gulp.src(files)
            .pipe(concat('jsmearhash.min.js'))
            .pipe(minify())
            // .pipe(inject.prepend(msg))
            .on("error", function (e) {
                console.log(e.toString());
                this.emit("end");
            })
            .pipe(gulp.dest('./dist/'))
    )
}
gulp.task("buildMin", gulp.series(buildMin));
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




function copyFiles(done){

    fs.copyFile('./dist/jsmearhash.min.js', './demo/jsmearhash.min.js', (err) => {
        if (err){
            throw err;
        } else {
            console.log('COPY: jsmearhash.min.js > demo/jsmearhash.min.js');
        }
    });


    fs.copyFile('./dist/jsmearhash.js', './demo/jsmearhash.js', (err) => {
        if (err){
            throw err;
        } else {
            console.log('COPY: jsmearhash.js TO demo/jsmearhash.js');
        }
    });


  // Gulp injecst the done and wants the done back... meh
  return done();
}
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
gulp.task("build", gulp.series(buildDev,buildMin,copyFiles));
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




// Watch
function watch() {
    gulp.watch(files, gulp.series(buildDev,buildMin,copyFiles))
}
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
gulp.task("watch",watch);
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
