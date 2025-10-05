// ======================================================
//  INIT
// ======================================================

document.addEventListener('DOMContentLoaded', initFilters);


// ======================================================
//  INIT FILTERS + SORT + SAVED STATE + HASH
// ======================================================

function initFilters() {
    const searchInput  = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const moduleFilter = document.getElementById('moduleFilter');
    const resetBtn = document.getElementById("reset-filters");
    const resetExp = document.getElementById("reset-expanded");
    const sortBtns = document.querySelectorAll('.sort-btn');
    const filterBtns = document.querySelectorAll('.filter-btn');

    restoreFilters();
    restoreSort();
    restoreExpandedState();

    searchInput?.addEventListener('input', filterTests);
    statusFilter?.addEventListener('change', filterTests);
    moduleFilter?.addEventListener('change', filterTests);

    searchInput?.addEventListener('keydown', e => {
        if (e.key === 'Escape') {
            searchInput.value = '';
            saveFilters();
            filterTests();
        }
    });

    filterBtns.forEach(btn => btn.addEventListener('click', () => {
        btn.classList.toggle('active');
        saveFilters();
        filterTests();
    }));

    sortBtns.forEach(btn => btn.addEventListener('click', () => {
        const wasActive = btn.classList.contains('active');
        sortBtns.forEach(b => b.classList.remove('active'));
        if (!wasActive) btn.classList.add('active');
        saveSort();
        filterTests();
    }));

    resetBtn?.addEventListener("click", () => {
        searchInput.value = "";
        clearSelect(statusFilter);
        clearSelect(moduleFilter);

        filterBtns.forEach(btn => btn.classList.remove("active"));
        document.querySelector('.filter-btn[data-filter="all"]')?.classList.add("active");

        sortBtns.forEach(b => b.classList.remove("active"));

        document.querySelector('.sort-btn[data-sort="name_asc"]')?.classList.add("active");

        saveFilters();
        saveSort();
        filterTests();
    });

    resetExp?.addEventListener("click", () => {
        const allTests = Array.from(document.querySelectorAll('.test')).filter(
            test => !test.querySelector(':scope > .test-content-multi')
        );

        if (!allTests.length) return;

        const anyOpened = allTests.some(test =>
            test.querySelector(':scope > .test-content.active')
        );

        const newState = !anyOpened;

        for (const test of allTests) {
            const header = test.querySelector(':scope > .test-header');
            const content = test.querySelector(':scope > .test-content');

            // Игнорируем test-header-multi / test-content-multi
            if (!header || header.classList.contains('test-header-multi')) continue;
            if (!content || content.classList.contains('test-content-multi')) continue;

            header.classList.toggle('expanded', newState);
            content.classList.toggle('active', newState);

            if (test.id) updateExpandedState(test.id, newState);
        }

        if (newState) {
            const firstId = allTests[0]?.id;
            if (firstId) history.replaceState({ openedId: firstId }, "", `#${firstId}`);
        } else {
            history.replaceState({}, "", location.pathname + location.search);
        }
    });

    filterTests();
}


// ======================================================
//  FILTER + SORT STATE SAVE
// ======================================================

function saveFilters(){
    const search = document.getElementById('searchInput')?.value||'';
    const status = getSelectedValues(document.getElementById('statusFilter'));
    const module = getSelectedValues(document.getElementById('moduleFilter'));
    const buttons = Array.from(document.querySelectorAll('.filter-btn.active')).map(b=>b.dataset.filter||'');
    localStorage.setItem("filters",JSON.stringify({search,status,module,buttons}));
}

function restoreFilters(){
    try{
        const stored = JSON.parse(localStorage.getItem("filters")||"{}");
        if(stored.search) document.getElementById('searchInput').value = stored.search;
        if(stored.status) Array.from(document.getElementById('statusFilter').options).forEach(o=>o.selected = stored.status.includes(o.value));
        if(stored.module) Array.from(document.getElementById('moduleFilter').options).forEach(o=>o.selected = stored.module.includes(o.value));
        if(stored.buttons) stored.buttons.forEach(f=>{
            const btn = document.querySelector(`.filter-btn[data-filter="${f}"]`);
            if(btn) btn.classList.add("active");
        });
    }catch{}
}

function saveSort(){
    const active = document.querySelector('.sort-btn.active')?.dataset.sort||'';
    localStorage.setItem("sort",active);
}

function restoreSort(){
    const sortValue = localStorage.getItem("sort")||"name_asc";
    document.querySelectorAll('.sort-btn').forEach(b=>b.classList.remove("active"));
    const btn = document.querySelector(`.sort-btn[data-sort="${sortValue}"]`);
    if(btn) btn.classList.add("active");
}


// ======================================================
//  FILTER UTILS
// ======================================================

function getSelectedValues(select) {
    if (!select) return [];
    const values = select.multiple
        ? Array.from(select.selectedOptions).map(o => o.value)
        : select.value ? [select.value] : [];
    return values.map(v => (v??'').toString().trim()).filter(v => v && v.toLowerCase() !== 'all');
}

function clearSelect(select) {
    if (!select) return;
    if (select.multiple) {
        Array.from(select.options).forEach(o => o.selected = false);
    } else {
        const hasAll = Array.from(select.options).some(o => o.value.toLowerCase() === 'all');
        select.value = hasAll ? 'all' : '';
    }
}

function normalizeStatus(s) { return (s??'').toString().trim().toUpperCase(); }

function matchesFilters(nameLC, statusRaw, moduleName, filters) {
    const statusU = normalizeStatus(statusRaw);
    if (filters.search && !nameLC.includes(filters.search)) return false;
    if (filters.status.length && !filters.status.includes(statusU)) return false;
    if (filters.module.length && !filters.module.includes(moduleName)) return false;
    if (filters.buttonStatuses.length && !filters.buttonStatuses.includes(statusU.toLowerCase())) return false;
    return true;
}


// ======================================================
//  SORT UTILS
// ======================================================

function getSortOptions() {
    const activeBtn = document.querySelector('.sort-btn.active');
    if (!activeBtn) return { field: 'name', order: 'asc' };
    const ds = (activeBtn.dataset.sort || 'none').toString();
    if (!ds || ds === 'none') return { field: 'name', order: 'asc' };
    const [field, order] = ds.split('_');
    return { field, order: order === 'desc' ? 'desc' : 'asc' };
}

function compareTests(a, b, field, order='asc') {
    let valA, valB;
    switch(field) {
        case 'name':
            valA = (a.dataset.test||'').toLowerCase();
            valB = (b.dataset.test||'').toLowerCase();
            break;
        case 'duration':
            valA = parseFloat(a.dataset.duration||'0')||0;
            valB = parseFloat(b.dataset.duration||'0')||0;
            break;
        case 'status':
            valA = (a.dataset.status||'').toUpperCase();
            valB = (b.dataset.status||'').toUpperCase();
            break;
        default: return 0;
    }
    if (valA < valB) return order==='asc'? -1:1;
    if (valA > valB) return order==='asc'? 1:-1;
    return 0;
}


// ======================================================
//  FILTER + SORT
// ======================================================

function filterTests() {
    const search = (document.getElementById('searchInput')?.value||'').toLowerCase().trim();
    const statusSelected = getSelectedValues(document.getElementById('statusFilter')).map(v=>v.toUpperCase());
    const moduleSelected = getSelectedValues(document.getElementById('moduleFilter'));
    const activeButtons = Array.from(document.querySelectorAll('.filter-btn.active'))
        .map(b => (b.dataset.filter||'').toLowerCase().trim())
        .filter(f => f && f !== 'all');

    const {field: sortField, order: sortOrder} = getSortOptions();
    const filters = {search, status: statusSelected, module: moduleSelected, buttonStatuses: activeButtons};

    const modules = document.querySelectorAll('.module');
    let modulesVisible = 0;

    modules.forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        const container = moduleEl.querySelector('.tests-list');
        if (!container) return;

        const topTests = Array.from(container.querySelectorAll(':scope > .test'));

        // 1) сортировка
        if(sortField){
            topTests.sort((a,b)=>compareTests(a,b,sortField,sortOrder));
            topTests.forEach(t=>container.appendChild(t));
        }

        // 2) фильтры
        let moduleHasVisible = false;
        topTests.forEach(test => {
            const isGroup = test.classList.contains('test-multi');
            const testName = (test.dataset.test||'').toLowerCase();
            let visible = false;

            if(isGroup){
                let subVisible = 0;
                test.querySelectorAll('.test-sub').forEach(sub=>{
                    const subName = (sub.dataset.test||'').toLowerCase();
                    const subStatus = sub.dataset.status;
                    const show = matchesFilters(subName, subStatus, moduleName, filters);
                    sub.style.display = show?'block':'none';
                    if(show) subVisible++;
                });
                visible = subVisible>0;
            } else {
                visible = matchesFilters(testName, test.dataset.status, moduleName, filters);
            }

            test.style.display = visible?'block':'none';
            if(visible) moduleHasVisible = true;
        });

        moduleEl.style.display = moduleHasVisible?'block':'none';
        if(moduleHasVisible) modulesVisible++;
    });

    // no results
    let noResults = document.getElementById('noResults');
    if(modulesVisible===0){
        if(!noResults){
            noResults = document.createElement('div');
            noResults.id='noResults';
            noResults.className='no-results';
            noResults.innerHTML='<i class="fas fa-search"></i><br>No tests match your filters';
            document.querySelector('.main-content')?.appendChild(noResults);
        }
    } else { noResults?.remove(); }
}


// ======================================================
//  UI-Toggles
// ======================================================

function toggleBlock(header){
    const content = header.nextElementSibling;
    if(!content) return;

    const el = header.closest(".test, .card");
    const isOpening = !content.classList.contains("active");

    header.classList.toggle("expanded");
    content.classList.toggle("active");

    if(el && el.id) updateExpandedState(el.id, isOpening);
}

function toggleAllTests() {
    const tests = document.querySelectorAll('.test-content');
    if (tests.length === 0) return;

    const hasOpen = Array.from(tests).some(t => t.classList.contains('active'));

    tests.forEach(t => {
        const header = t.previousElementSibling;
        if (!header) return;

        if (hasOpen) {
            t.classList.remove('active');
            header.classList.remove('expanded');
        } else {
            t.classList.add('active');
            header.classList.add('expanded');
        }

        if (hasOpen && window.location.hash) {
            history.replaceState(null, null, ' ');
        }
    });
}

//function toggleStacktrace(el) {
//    el.classList.toggle("expanded");
//    el.nextElementSibling?.classList.toggle("active");
//}

function toggleStep(header) {
    const step = header.closest('.step');
    if (!step) return;

    const body = step.querySelector('.step-body');
    const content = step.querySelector('.step-content');
    const isActive = header.classList.contains('expanded');

    body?.classList.toggle('active', !isActive);
    header.classList.toggle('expanded', !isActive);
    content?.classList.toggle('expanded', !isActive);
    content?.classList.toggle('active', !isActive);
}

function switchTab(btn, tabName) {
    const tabsContainer = btn.closest('.tabs');
    if (!tabsContainer) return;

    tabsContainer.querySelectorAll('.tab-btn').forEach(tab => tab.classList.remove('active'));
    tabsContainer.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    btn.classList.add('active');
    tabsContainer.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
}


// ======================================================
//  Navigation / Hash
// ======================================================

function toggleTestAndHash(header){
    const el = header.closest(".test, .card");
    if(!el||!el.id) return;
    const content = header.nextElementSibling;
    const isOpening = !content.classList.contains("active");
    toggleBlock(header);
    updateExpandedState(el.id, isOpening);
    history.pushState(isOpening?{openedId:el.id}:{},"",isOpening?`#${el.id}`:location.pathname+location.search);
}

function updateExpandedState(id,isOpen){
    let state={};
    try{ state=JSON.parse(localStorage.getItem("expandedTests")||"{}"); }catch{}
    state[id]=isOpen;
    localStorage.setItem("expandedTests",JSON.stringify(state));
}

function restoreExpandedState(){
    let state={};
    try{ state=JSON.parse(localStorage.getItem("expandedTests")||"{}"); }catch{}
    Object.keys(state).forEach(id=>{
        const el = document.getElementById(id);
        if(!el) return;
        const header = el.querySelector(":scope > .header, :scope > .test-header, :scope > .test-header-multi");
        const content = el.querySelector(":scope > .content, :scope > .test-content");
        if(!header||!content) return;
        if(state[id]){
            header.classList.add("expanded");
            content.classList.add("active");
        } else {
            header.classList.remove("expanded");
            content.classList.remove("active");
        }
    });
}

function expandTestAndParents(el){
    if(!el) return;
    let current = el;
    while(current){
        const header = current.querySelector(":scope > .test-header, :scope > .test-header-multi, :scope > .header");
        const content = current.querySelector(":scope > .test-content, :scope > .content");
        header?.classList.add("expanded");
        content?.classList.add("active");
        if(current.id) updateExpandedState(current.id,true);
        current = current.parentElement?.closest(".test, .card");
    }
}

function resetAllBlocks(){
    document.querySelectorAll(".test-content").forEach(c=>c.classList.remove("active"));
    document.querySelectorAll(".test-header").forEach(h=>h.classList.remove("expanded"));
    localStorage.removeItem("expandedTests");
}

// ===================== HASH HANDLING =====================
window.addEventListener("load",()=>{
    restoreExpandedState();
    const hash = location.hash.slice(1);
    if(hash){
        const el = document.getElementById(hash);
        if(el){
            el.classList.add("highlight");
            el.scrollIntoView({behavior:"smooth"});
            expandTestAndParents(el);
        }
    }
});

window.addEventListener("popstate",event=>{
    restoreExpandedState();
    const id = event.state?.openedId;
    if(id){
        const el = document.getElementById(id);
        if(el){
            el.classList.add("highlight");
            el.scrollIntoView({behavior:"smooth"});
            expandTestAndParents(el);
        }
    }
});


// ======================================================
//  Attachment Modal
// ======================================================

const modal          = document.getElementById('attachmentModal');
const titleEl        = document.getElementById('modalTitle');
const image          = document.getElementById('modalImage');
const imageContainer = document.getElementById('imageContainer');
const textPreview    = document.getElementById('modalText');
const pdfContainer   = document.getElementById('modalPDF');
const download       = document.getElementById('modalDownload');

let scale = 1;

function openAttachment(name, type) {
    const path = `./attachments/${name}`;

    // Сброс состояния
    scale = 1;
    if (image) image.style.transform = 'scale(1)';
    if (image) image.src = '';
    if (pdfContainer) pdfContainer.src = '';
    if (textPreview) textPreview.textContent = '';
    [imageContainer, textPreview, pdfContainer, download].forEach(el => { if (el) el.style.display = 'none'; });

    if (titleEl) titleEl.textContent = name;

    if (type && type.startsWith('image/')) {
        if (image) image.src = path;
        if (imageContainer) imageContainer.style.display = 'block';
    } else if (type === 'application/pdf') {
        if (pdfContainer) pdfContainer.src = path;
        if (pdfContainer) pdfContainer.style.display = 'block';
    } else if (type && type.startsWith('text/') || /\.(json|log|txt|py|md)$/i.test(name)) {
        fetch(path)
            .then(res => res.text())
            .then(text => {
                if (textPreview) textPreview.textContent = text;
                if (textPreview) textPreview.style.display = 'block';
            })
            .catch(() => {
                if (textPreview) textPreview.textContent = '[Ошибка загрузки текста]';
                if (textPreview) textPreview.style.display = 'block';
            });
    } else {
        if (download) {
            download.href = path;
            download.style.display = 'inline-block';
        }
    }

    if (modal) modal.style.display = 'block';
}

function closeModal(event) {
    if (!modal) return;
    if (event.target.id === modal.id || event.target.classList.contains('close')) {
        modal.style.display = 'none';
    }
}

// Zoom + Drag (защита, если контейнера нет)
if (imageContainer) {
    imageContainer.addEventListener('wheel', (e) => {
        e.preventDefault();
        scale = Math.min(Math.max(scale + e.deltaY * -0.001, 0.5), 5);
        if (image) image.style.transform = `scale(${scale})`;
    });

    let isDragging = false, startX = 0, startY = 0, scrollLeft = 0, scrollTop = 0;

    imageContainer.addEventListener('mousedown', e => {
        isDragging = true;
        startX = e.pageX;
        startY = e.pageY;
        scrollLeft = imageContainer.scrollLeft;
        scrollTop = imageContainer.scrollTop;
        imageContainer.style.cursor = 'grabbing';
    });

    imageContainer.addEventListener('mousemove', e => {
        if (!isDragging) return;
        imageContainer.scrollLeft = scrollLeft - (e.pageX - startX);
        imageContainer.scrollTop  = scrollTop - (e.pageY - startY);
    });

    ['mouseup', 'mouseleave'].forEach(evt =>
        imageContainer.addEventListener(evt, () => {
            isDragging = false;
            imageContainer.style.cursor = 'grab';
        })
    );
}


// ======================================================
//  Theme
// ======================================================

const root = document.documentElement;
const themeToggle = document.getElementById("themeToggle");
const savedTheme = localStorage.getItem("theme");

if (root) {
    root.setAttribute(
        "data-theme",
        savedTheme || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    );
}

themeToggle?.addEventListener("click", () => {
    const current = root.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
});
