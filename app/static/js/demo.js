/**
 * Created by wanglianjun on 16-5-16.
 */
//返回顶部
$(function() {
    $(window).scroll(function() {
        if ($(window).scrollTop() > 1000)
            $('div.go-top').show();
        else
            $('div.go-top').hide();
    });
    $('div.go-top').click(function() {
        $('html, body').animate({scrollTop: 0}, 800);
    });
});
//隐藏博客文章部分内容
function getByClass(oParent, sClass) {
if (oParent.getElementsByClassName) {
return oParent.getElementsByClassName(sClass);
} else { //IE 8 7 6
var arr = [];
var reg = new RegExp('\\b' + sClass + '\\b');
var aEle = oParent.getElementsByTagName('*');
for (var i = 0; i < aEle.length; i++) {
if (reg.test(aEle[i].className)) {
arr.push(aEle[i]);
}
}
return arr;
}
}
function testAuto() {
    if(window.location.pathname.indexOf("user")>-1 || window.location.pathname.indexOf("post")>-1 ){
        return false;
    }else {
        var textName = getByClass(document, 'post-content');
        for (var i = 0; i < textName.length; i++) {
        var nowLeng = textName[i].innerHTML.length;
        if ( nowLeng > 150 ) {
        var nowWord = textName[i].innerHTML.substr(0, 150);
    textName[i].innerHTML = nowWord;}}
    }
}
$(document).ready(testAuto());
// 关注/被关注切换
$(function(){
    var $fw = $('#followers');
    var $fd = $('#followed');
    if(window.location.href.indexOf('follwers')){
        $fd.hide();
    }else {
        $fw.hide();
    }
});
//图片展示
$(function(){
    $('.showform').hide();
    $('#showform').mouseenter(function(){
        $('.showform').stop().fadeIn();
    }).mouseleave(function(){
        $('.showform').stop().fadeOut();
    });
});
//轮播效果
 $(function(){
          $('#myCarousel').carousel({
            interval: 2000,ride:carousel
});
      // 初始化轮播
         $("#myCarousel").carousel('cycle');
      // 停止轮播
         $("#myCarousel").carousel('pause');
      // 循环轮播到上一个项目
         $("#myCarousel").carousel('prev');
      // 循环轮播到下一个项目
         $("#myCarousel").carousel('next');
      // 循环轮播到某个特定的帧
         $("#myCarousel").carousel(0);
         $("#myCarousel").carousel(1);
         $("#myCarousel").carousel(2);
   });
