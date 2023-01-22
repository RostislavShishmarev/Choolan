function updateFirstButtonWidth(event) {
    let container = document.getElementsByClassName('look-or-load-section')[0];
    if (container === null) {
        return;
    }
    let width = container.lastElementChild.clientWidth;
    container.firstElementChild.setAttribute("style", `width:${width}px;`);;
}


updateFirstButtonWidth(null);
window.onresize = updateFirstButtonWidth;
