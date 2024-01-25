function openNav() {
    document.getElementById("sidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.getElementById("openBtn").style.display = "none";
}

function closeNav() {
    document.getElementById("sidebar").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
    document.getElementById("openBtn").style.display = "block";
}
function toggleSelection(link) {
    const checkbox = link.querySelector('input[type="checkbox"]');
    checkbox.checked = !checkbox.checked;
    link.classList.toggle('selected', checkbox.checked);
}