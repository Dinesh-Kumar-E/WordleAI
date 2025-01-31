const colors = ['#787c7e', '#6aaa64', '#c9b458']; // grey, green, yellow

function getRandomColor() {
    return colors[Math.floor(Math.random() * colors.length)];
}

const boxes = document.querySelectorAll('.box');

boxes.forEach(box => {
    box.style.backgroundColor = getRandomColor();
});

setInterval(() => {
    boxes.forEach(box => {
        box.style.backgroundColor = getRandomColor();
    });
}, 800);

