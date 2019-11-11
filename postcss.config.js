const purgecss = require("@fullhuman/postcss-purgecss")({
  content: [
    "./assets/js/*.js",
    "./assets/css/*.css",
    "./subscriptions/templates/registration/*.html",
    "./subscriptions/templates/subscriptions/*.html",
  ],

  defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || []
});

module.exports = {
  plugins: [
    require("tailwindcss"),
    require("autoprefixer"),
    ...process.env.NODE_ENV === "production"
    ? [purgecss]
    : []
  ],
};
