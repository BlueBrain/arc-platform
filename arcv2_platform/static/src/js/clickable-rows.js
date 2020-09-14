/* Making entire table row clickable */

function isOrChildOf (target, selector) {
    const selectorNodes = [].slice.call(document.querySelectorAll(selector));
    return selectorNodes.some((el) => el === target || el.contains(target));
}


function addClickHandler(tr) {
    tr.addEventListener('click', (evt) => {
        if (isOrChildOf(evt.srcElement, '.row--no-click')) return;

        window.location = tr.getAttribute('data-href');
    });
}

const trs = document.querySelectorAll('table tbody tr.clickable');

trs.forEach(addClickHandler);
