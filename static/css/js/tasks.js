document.querySelectorAll(".task-node").forEach(node => {
    node.onmousedown = function (e) {
        const shiftX = e.clientX - node.getBoundingClientRect().left;
        const shiftY = e.clientY - node.getBoundingClientRect().top;

        function moveAt(pageX, pageY) {
            node.style.left = pageX - shiftX + 'px';
            node.style.top = pageY - shiftY + 'px';
        }

        function onMouseMove(event) {
            moveAt(event.pageX, event.pageY);
        }

        document.addEventListener('mousemove', onMouseMove);

        node.onmouseup = function () {
            document.removeEventListener('mousemove', onMouseMove);
            node.onmouseup = null;
        };
    };

    node.ondragstart = function () {
        return false;
    };
});