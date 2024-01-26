
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
    updateSelectionOnServer(checkbox.id, checkbox.checked);
}
function updateSelectionOnServer(checkboxId, selected) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/update_selection', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send(`checkbox_id=${checkboxId}&selected=${selected}&username=${encodeURIComponent('{{ username }}')}`);
}
function uncheckAll() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
        updateSelectionOnServer(checkbox.id, false);
    });
}

function go(){
    window.location.href = "dashboard";
}