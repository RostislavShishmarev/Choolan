function copyEmail() {
    let element = document.getElementById('email-link');
    copyTextToBoofer(element.getAttribute('value'), element);
  
    let info = document.getElementById('email-copy-message');
    info.innerHTML = "Адрес скопирован";
    setTimeout(() => {
      info.innerHTML = "";
    }, 1000);
  }
  