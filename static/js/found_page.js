function updateFirstButtonWidth(event) {
    let container = document.getElementsByClassName('look-or-load-section')[0];
    if (container === null) {
        return;
    }
    let width = container.lastElementChild.clientWidth + 4;
    container.firstElementChild.setAttribute("style", `min-width:${width}px;`);;
}


updateFirstButtonWidth(null);
window.onresize = updateFirstButtonWidth;
