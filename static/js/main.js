function copyTextToBoofer(text, element) {
  try {
    navigator.clipboard.writeText(text);
    console.log("Used normal copy method.");
  } catch (err) {
    element.select();
    document.execCommand("copy");
    clearSelection();
    console.log("Used deprecated copy method.");
  }
}

function clearSelection() {
  if (window.getSelection) {
    window.getSelection().removeAllRanges();
  } else if (document.selection) {
    document.selection.empty();
  }
}
