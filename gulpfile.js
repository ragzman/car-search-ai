const gulp = require('gulp');
const ts = require('gulp-typescript');

const tsProject = ts.createProject('tsconfig.json');

gulp.task('compile', () => {
  return gulp.src('templates/index.ts')
    .pipe(tsProject())
    .pipe(gulp.dest('dist'));
});

gulp.task('watch', () => {
  gulp.watch('templates/index.ts', gulp.series('compile'));
});

gulp.task('default', gulp.series('compile'));
