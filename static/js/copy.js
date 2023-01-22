function copyFrom(id, message_id) {
  // Очистка уведомлений, чтобы они там не оставались
  for (let m_id of ["key-copy-message", "link-copy-message"]) {
    let el = document.getElementById(m_id);
    el.innerHTML = "";
  }

  element = document.getElementById(id);
  try {
    navigator.clipboard.writeText(element.value);
    console.log("Used normal copy method.");
  } catch (err) {
    element.select();
    document.execCommand("copy");
    clearSelection();
    console.log("Used deprecated copy method.");
  }

  info = document.getElementById(message_id);
  info.innerHTML = "Скопировано!";
  setTimeout(() => {
    info.innerHTML = "";
  }, 1000);
}


function clearSelection() {
  if (window.getSelection) {
    window.getSelection().removeAllRanges();
  } else if (document.selection) {
    document.selection.empty();
  }
}
