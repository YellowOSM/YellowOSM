const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const StyleLintPlugin = require('stylelint-webpack-plugin');

module.exports = {
  mode: 'development',
  entry: {
    bundle: "./js/bundle.js"
  },
  output: {
    path: __dirname + '/dist',
    publicPath: '/dist',
    filename: '[name].js'
  },
  plugins: [
    new CopyWebpackPlugin([{
      from: 'img/',
      to: 'img/'
    }]),
    // new webpack.ProvidePlugin({
    //   $: 'jquery',
    //   jQuery: 'jquery',
    //   'window.jQuery': 'jquery'
    // }),
    new StyleLintPlugin({
      configFile: '.stylelintrc',
      files: [
        'scss/!(font-awesome)/*.scss',
        'scss/*.scss'
      ],
      failOnError: false,
      quiet: false
    })
  ],
  // externals: {
  //   jquery: 'jQuery'
  // },
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
          'style-loader?sourceMap',
          'css-loader?sourceMap',
          'postcss-loader?sourceMap',
          'sass-loader?sourceMap'
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
            publicPath: '/dist/fonts/'
          }
        }]
      },
      {
        test: /\.(png|gif|jp(e)?g)$/,
        loader: 'url-loader?limit=100000'
      }
    ]
  }
};
