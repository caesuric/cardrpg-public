var path = require('path');
module.exports = {
  entry: {
    login: './web_es5/login.js',
    main: './web_es5/main.js'
  },
  output: {
    path: path.resolve(__dirname,'web/js'),
    filename: '[name].js',
    sourcePrefix: ''
  },
  module: {
    loaders: [
      {
        test: /\.css$/,
        loader: 'style-loader!css-loader'
      },
      {
        test: /\.(png|gif|jpg|jpeg|wav)$/,
        loader: 'file-loader'
      },
      {
        test: /\.(eot|svg|ttf|woff(2)?)(\?v=\d+\.\d+\.\d+)?/,
        loader: 'url-loader'
      }
    ],
    unknownContextCritical: false
  },
  devtool: 'source-map',
  resolve: {
    alias: {
      jquery: 'jquery/src/jquery'
    },
    modules: [
      'node_modules',
      path.resolve(__dirname, 'web_es5/lib'),
      path.resolve(__dirname, 'web_es5/css'),
      path.resolve(__dirname, 'web_es5/assets/images'),
      path.resolve(__dirname, 'web_es5/assets/sounds')
    ]
  }
};
