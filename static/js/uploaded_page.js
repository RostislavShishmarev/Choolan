function copyFrom(id, message_id) {
  // Очистка уведомлений, чтобы они там не оставались
  for (let m_id of ["key-copy-message", "link-copy-message"]) {
    let el = document.getElementById(m_id);
    el.innerHTML = "";
  }

  let element = document.getElementById(id);
  copyTextToBoofer(element.value, element);

  let info = document.getElementById(message_id);
  info.innerHTML = "Скопировано!";
  setTimeout(() => {
    info.innerHTML = "";
  }, 1000);
}
