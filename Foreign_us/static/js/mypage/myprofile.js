function setprofile(event) {
    var reader = new FileReader();
    reader.onload = function (event) {
        $('.profile-img').attr('src', event.target.result);
    }
    reader.readAsDataURL(event.target.files[0]);
}

function setCover() {
    var reader = new FileReader();
    reader.onload = function (event) {
        $('.back-pic').show();
        $('.cover-pic').remove();
        $('.back-pic').attr('src', event.target.result);
        console.log(event.target.result)
    }
    reader.readAsDataURL(event.target.files[0]);
}











//