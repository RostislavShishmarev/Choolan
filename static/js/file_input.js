let inputs = document.querySelectorAll(".ch-file-input");
Array.prototype.forEach.call(inputs, function (input) {
  let label = input.nextElementSibling;
  let labelVal = label.querySelector(".ch-file-input-text").innerText;
  input.addEventListener("change", function (e) {
    if (this.files && this.files.length >= 1) {
      label.querySelector(".ch-file-input-text").innerText =
        "Выбран файл: " + this.files[0].name;
    } else {
      label.querySelector(".ch-file-input-text").innerText = labelVal;
    }
  });
});
