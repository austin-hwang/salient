jtitle.onkeyup = function(e) {
    if(e.keyCode == 13) {
      getData(e.target.value);
    }
  }

function getData(){
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:1234/send-data', true);
    xhr.onload = function (e) {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          console.log(xhr.responseText);
          var result = xhr.responseText;
          document.getElementById("jsonFile").innerHTML = result;
        }
    }
    };
    xhr.send();
}