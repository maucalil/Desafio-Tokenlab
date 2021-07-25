document.querySelector('#end').onkeyup = function () {
    if(document.querySelector('#end').value !== '' && document.querySelector('#name').value !== '' && document.querySelector('#date').value !== ''
      && document.querySelector('#description').value !== '' && document.querySelector('#start').value !== '') {
        document.querySelector('#submit').disabled = false;
    }
    else {
        document.querySelector('#submit').disabled = true;
    }
};
