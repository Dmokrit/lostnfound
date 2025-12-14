function reportLost(){
    const name = document.getElementById('lostName').value;
    const desc = document.getElementById('lostDesc').value;
    const file = document.getElementById('lostPhoto').files[0];
    if (!name || !desc) return alert('Fill all fields');

    if(file){
        const reader = new FileReader();
        reader.onload = function(e){
            saveLost(name, desc, e.target.result);
        };
        reader.readAsDataURL(file);
    } else {
        saveLost(name, desc, null);
    }
}

function saveLost(name, desc, photo){
    const lost = JSON.parse(localStorage.getItem('lost')) || [];
    lost.push({ name, desc, user: currentUser, photo });
    localStorage.setItem('lost', JSON.stringify(lost));
    document.getElementById('lostName').value='';
    document.getElementById('lostDesc').value='';
    document.getElementById('lostPhoto').value='';
    loadItems();
}

function addFound(){
    const name = document.getElementById('foundName').value;
    const desc = document.getElementById('foundDesc').value;
    const file = document.getElementById('foundPhoto').files[0];
    if (!name || !desc) return alert('Fill all fields');

    if(file){
        const reader = new FileReader();
        reader.onload = function(e){
            saveFound(name, desc, e.target.result);
        };
        reader.readAsDataURL(file);
    } else {
        saveFound(name, desc, null);
    }
}

function saveFound(name, desc, photo){
    const found = JSON.parse(localStorage.getItem('found')) || [];
    found.push({ name, desc, claimed: false, photo });
    localStorage.setItem('found', JSON.stringify(found));
    document.getElementById('foundName').value='';
    document.getElementById('foundDesc').value='';
    document.getElementById('foundPhoto').value='';
    loadItems();
}

function loadItems(){
    const lostList = document.getElementById('lostList');
    const foundList = document.getElementById('foundList');
    lostList.innerHTML = '';
    foundList.innerHTML = '';

    const lost = JSON.parse(localStorage.getItem('lost')) || [];
    const found = JSON.parse(localStorage.getItem('found')) || [];

    lost.forEach(item=>{
        lostList.innerHTML += `<div class="item">
            <strong>${item.name}</strong>
            <p>${item.desc}</p>
            ${item.photo?`<img src="${item.photo}" width="200"/>`:''}
            <small>Reported by ${item.user}</small>
        </div>`;
    });

    found.forEach((item,i)=>{
        foundList.innerHTML += `<div class="item">
            <strong>${item.name}</strong>
            <p>${item.desc}</p>
            ${item.photo?`<img src="${item.photo}" width="200"/>`:''}
            ${item.claimed?`<small>Claimed by ${item.claimedBy}</small>`:`<button onclick="claimItem(${i})">Claim</button>`}
        </div>`;
    });
}

