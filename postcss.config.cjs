module.exports = {
  // use parser, since syntax expects to output back to the same file type, so SCSS comments will
  // not be transpiled to CSS comments
  parser: "postcss-scss",
  plugins: {
    stylelint: {},
    "postcss-import": {},
    "postcss-nested": {}, // put early to avoid issues
    "postcss-preset-env": {},
    autoprefixer: {},
    "postcss-advanced-variables": {},
  },
};
