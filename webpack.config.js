var path = require("path");
var BundleTracker = require("webpack-bundle-tracker");

module.exports = {
  mode: "development",
  context: __dirname,
  entry: "./assets/js/index",
  output: {
    path: path.resolve("./assets/webpack_bundles/"),
    filename: "[name]-[hash].js"
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        exclude: /node_modules/,
        use: ["style-loader", "css-loader", "postcss-loader"],
      },
    ],
  },
  plugins: [
    new BundleTracker({filename: "./webpack-stats.json"})
  ],
}
