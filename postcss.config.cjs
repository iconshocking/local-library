module.exports = {
  // use parser, since syntax expects to output back to the same file type, so SCSS comments will
  // not be transpiled to CSS comments
  parser: "postcss-scss",
  plugins: {
    "postcss-preset-env": {},
    stylelint: {},
    "postcss-nesting": {},
    autoprefixer: {},
    "postcss-import": {},
    "postcss-advanced-variables": {},
  },
};
