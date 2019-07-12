const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ImageminPlugin = require('imagemin-webpack-plugin').default;
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");

module.exports = function (env) {
  return {
    mode: 'production',
    entry: {
      bundle: "./js/bundle.js"
    },
    devtool: 'source-map',
    output: {
      path: __dirname + '/dist-prod',
      publicPath: '/content/themes/frankowitsch/dist-prod/',
      filename: '[name].js'
    },
    plugins: [
      new CopyWebpackPlugin([{
        from: 'img/',
        to: 'img/'
      }]),
      new ImageminPlugin({test: /\.(jpe?g|png|gif|svg)$/i}),
      new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        'window.jQuery': 'jquery',
      }),
      new MiniCssExtractPlugin({
        filename: "styles.css",
      })
    ],
    optimization: {
      minimizer: [
        new UglifyJsPlugin({
          cache: true,
          parallel: true,
          uglifyOptions: {
            output: { comments: false }
          }
        }),
        new OptimizeCSSAssetsPlugin({})
      ]
    },
    externals: {
      jquery: 'jQuery'
    },
    resolve: {
      alias: {
        'select2': 'select2/dist/js/select2.full.js',
      },
    },
    module: {
      rules: [
        {
          test: [/\.js$/],
          exclude: /node_modules\/(?!(dom7|swiper)\/).*/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['env']
            }
          }
        },
        {
          test: /\.(sa|sc|c)ss$/,
          use: [
            {
              loader: MiniCssExtractPlugin.loader,
              options: {}
            },
            'css-loader',
            'postcss-loader',
            'sass-loader'
          ],
          exclude: /node_modules/
        },
        {
          test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
          use: [{
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/',
              publicPath: '/content/themes/frankowitsch/dist-prod/fonts/'
            }
          }]
        },
        {
          test: /\.(png|gif|jp(e)?g)$/,
          loader: 'url-loader?limit=100000'
        }
      ]
    }
  }
};
