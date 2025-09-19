const Jimp = require('jimp');
const fs = require('fs');

// 读取jpg文件并转换为png，然后保存
Jimp.read('frontend/public/favicon.ico')
  .then(image => {
    // 调整大小为常见的favicon尺寸
    return image.resize(32, 32).write('frontend/public/favicon.png');
  })
  .then(() => {
    console.log('图片已转换为PNG格式');
  })
  .catch(err => {
    console.error('转换过程中出错:', err);
  });