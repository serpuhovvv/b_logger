// ======================================================
//  INIT
// ======================================================

document.addEventListener('DOMContentLoaded', initPage);


// ======================================================
//  INIT FILTERS + SORT + SAVED STATE + HASH
// ======================================================

function initPage() {
    const searchInput  = getElById('searchInput');
    const statusFilter = getElById('statusFilter');
    const moduleFilter = getElById('moduleFilter');
    const resetFilters = getElById('reset-filters');
    const resetSorting = getElById('reset-sorting');
    const resetExp     = getElById('reset-expanded');
    const sortBtns     = getAll('.sort-btn');
    const filterBtns   = getAll('.filter-btn');

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
        toggleClass(btn, 'active');
        saveFilters();
        filterTests();
    }));

    sortBtns.forEach(btn => btn.addEventListener('click', () => {
        const wasActive = btn.classList.contains('active');
        sortBtns.forEach(b => toggleClass(b, 'active', false));
        if (!wasActive) toggleClass(btn, 'active', true);
        saveSort();
        filterTests();
    }));

    resetFilters?.addEventListener("click", () => {
        searchInput.value = "";
        clearSelect(statusFilter);
        clearSelect(moduleFilter);

        filterBtns.forEach(btn => toggleClass(btn, "active", false));
        toggleClass(document.querySelector('.filter-btn[data-filter="all"]'), "active", true);

        saveFilters();
        filterTests();
    });

    resetSorting?.addEventListener("click", () => {
        sortBtns.forEach(b => toggleClass(b, "active", false));
        toggleClass(document.querySelector('.sort-btn[data-sort="name_asc"]'), "active", true);

        saveSort();
        filterTests();
    });

    resetExp?.addEventListener("click", () => {
        const allTests = getAll('.test').filter(
            test => !test.querySelector(':scope > .test-content-multi')
        );

        if (!allTests.length) return;

        const anyOpened = allTests.some(test =>
            test.querySelector(':scope > .test-content.active')
        );

        const newState = !anyOpened;

        for (const test of allTests) {
            const header  = test.querySelector(':scope > .test-header');
            const content = test.querySelector(':scope > .test-content');

            if (!header || header.classList.contains('test-header-multi')) continue;
            if (!content || content.classList.contains('test-content-multi')) continue;

            toggleClass(header, 'expanded', newState);
            toggleClass(content, 'active', newState);

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

function saveFilters() {
    const search  = getElById('searchInput')?.value || '';
    const status  = getSelectedValues(getElById('statusFilter'));
    const module  = getSelectedValues(getElById('moduleFilter'));
    const buttons = getAll('.filter-btn.active').map(b => b.dataset.filter || '');
    saveToStorage("filters", { search, status, module, buttons });
}

function restoreFilters() {
    try {
        const stored = loadFromStorage("filters", {});
        if (stored.search) getElById('searchInput').value = stored.search;

        if (stored.status) {
            Array.from(getElById('statusFilter').options).forEach(o => o.selected = stored.status.includes(o.value));
        }

        if (stored.module) {
            Array.from(getElById('moduleFilter').options).forEach(o => o.selected = stored.module.includes(o.value));
        }

        if (stored.buttons) {
            stored.buttons.forEach(f => {
                const btn = getElBySelector(`.filter-btn[data-filter="${f}"]`);
                toggleClass(btn, "active", true);
            });
        }
    } catch {}
}

function saveSort() {
    const active = getElBySelector('.sort-btn.active')?.dataset.sort || '';
    saveToStorage("sort", active);
}

function restoreSort() {
    const sortValue = loadFromStorage("sort", "name_asc");
    getAll('.sort-btn').forEach(b => b.classList.remove("active"));
    const btn = getElBySelector(`.sort-btn[data-sort="${sortValue}"]`);
    if (btn) btn.classList.add("active");
}

// ======================================================
//  FILTER UTILS
// ======================================================

function getSelectedValues(select) {
    if (!select) return [];
    const values = select.multiple
        ? Array.from(select.selectedOptions).map(o => o.value)
        : select.value ? [select.value] : [];
    return values.map(v => (v ?? '').toString().trim()).filter(v => v && v.toLowerCase() !== 'all');
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

function normalizeStatus(s) { return (s ?? '').toString().trim().toUpperCase(); }

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
    const activeBtn = getElBySelector('.sort-btn.active');
    if (!activeBtn) return { field: 'name', order: 'asc' };
    const ds = (activeBtn.dataset.sort || 'none').toString();
    if (!ds || ds === 'none') return { field: 'name', order: 'asc' };
    const [field, order] = ds.split('_');
    return { field, order: order === 'desc' ? 'desc' : 'asc' };
}

const STATUS_ORDER_ASC  = ['FAILED', 'BROKEN', 'PASSED', 'SKIPPED'];
const STATUS_ORDER_DESC = ['PASSED', 'FAILED', 'BROKEN', 'SKIPPED'];

function compareTests(a, b, field, order = 'asc') {
    let valA, valB;
    switch (field) {
        case 'name':
            valA = (a.dataset.test || '').toLowerCase();
            valB = (b.dataset.test || '').toLowerCase();
            break;
        case 'duration':
            valA = parseFloat(a.dataset.duration || '0') || 0;
            valB = parseFloat(b.dataset.duration || '0') || 0;
            break;
        case 'status':
            valA = (a.dataset.status || '').toUpperCase();
            valB = (b.dataset.status || '').toUpperCase();
            const orderArr = order === 'asc' ? STATUS_ORDER_ASC : STATUS_ORDER_DESC;
            return orderArr.indexOf(valA) - orderArr.indexOf(valB);
        default:
            return 0;
    }
    if (valA < valB) return order === 'asc' ? -1 : 1;
    if (valA > valB) return order === 'asc' ? 1 : -1;
    return 0;
}

// ======================================================
//  FILTER + SORT
// ======================================================

function filterTests() {
    const search = (getElById('searchInput')?.value||'').toLowerCase().trim();
    const statusSelected = getSelectedValues(getElById('statusFilter')).map(v=>v.toUpperCase());
    const moduleSelected = getSelectedValues(getElById('moduleFilter'));
    const activeButtons = getAll('.filter-btn.active')
        .map(b => (b.dataset.filter||'').toLowerCase().trim())
        .filter(f => f && f !== 'all');

    const {field: sortField, order: sortOrder} = getSortOptions();
    const filters = {search, status: statusSelected, module: moduleSelected, buttonStatuses: activeButtons};

    const modules = getAll('.module');
    let modulesVisible = 0;

    modules.forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        const container = getElBySelector('.tests-list', moduleEl);
        if (!container) return;

        const topTests = getAll(':scope > .test', container);

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
                getAll('.test-sub', test).forEach(sub=>{
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

        toggleClass(moduleEl, 'hidden', !moduleHasVisible);
        if(moduleHasVisible) modulesVisible++;
    });

    // no results
    let noResults = getElById('noResults');
    if(modulesVisible===0){
        if(!noResults){
            noResults = document.createElement('div');
            noResults.id='noResults';
            noResults.className='no-results';
            noResults.innerHTML='<i class="fas fa-search"></i><br>No tests match your filters';
            getElBySelector('.main-content')?.appendChild(noResults);
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
    const tests = getAll('.test-content');
    if (tests.length === 0) return;

    const hasOpen = tests.some(t => t.classList.contains('active'));

    tests.forEach(t => {
        const header = t.previousElementSibling;
        if (!header) return;

        toggleClass(t, 'active', !hasOpen);
        toggleClass(header, 'expanded', !hasOpen);

        if (hasOpen && window.location.hash) {
            history.replaceState(null, null, ' ');
        }
    });
}

//function toggleStacktrace(el) {
//    toggleClass(el, "expanded");
//    el.nextElementSibling && toggleClass(el.nextElementSibling, "active");
//}

function toggleStep(header) {
    const step = header.closest('.step');
    if (!step) return;

    const body = getElBySelector('.step-body', step);
    const content = getElBySelector('.step-content', step);
    const isActive = header.classList.contains('expanded');

    toggleClass(body, 'active', !isActive);
    toggleClass(header, 'expanded', !isActive);
    toggleClass(content, 'expanded', !isActive);
    toggleClass(content, 'active', !isActive);
}

function switchTab(btn, tabName) {
    const tabsContainer = btn.closest('.tabs');
    if (!tabsContainer) return;

    getAll('.tab-btn', tabsContainer).forEach(tab => toggleClass(tab, 'active', false));
    getAll('.tab-content', tabsContainer).forEach(content => toggleClass(content, 'active', false));

    toggleClass(btn, 'active', true);
    const tabContent = getElBySelector(`[data-tab="${tabName}"]`, tabsContainer);
    toggleClass(tabContent, 'active', true);
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
    history.pushState(isOpening ? {openedId: el.id} : {}, "", isOpening ? `#${el.id}` : location.pathname + location.search);
}

function updateExpandedState(id,isOpen){
    let state = {};
    try { state = JSON.parse(localStorage.getItem("expandedTests") || "{}"); } catch {}
    state[id] = isOpen;
    localStorage.setItem("expandedTests", JSON.stringify(state));
}

function restoreExpandedState(){
    let state = {};
    try { state = JSON.parse(localStorage.getItem("expandedTests") || "{}"); } catch {}
    Object.keys(state).forEach(id => {
        const el = getElById(id);
        if(!el) return;

        const header = getElBySelector(":scope > .header, :scope > .test-header, :scope > .test-header-multi", el);
        const content = getElBySelector(":scope > .content, :scope > .test-content", el);
        if(!header||!content) return;

        toggleClass(header, "expanded", state[id]);
        toggleClass(content, "active", state[id]);
    });
}

function expandTestAndParents(el){
    if(!el) return;
    let current = el;
    while(current){
        const header = getElBySelector(":scope > .test-header, :scope > .test-header-multi, :scope > .header", current);
        const content = getElBySelector(":scope > .test-content, :scope > .content", current);
        toggleClass(header, "expanded", true);
        toggleClass(content, "active", true);
        if(current.id) updateExpandedState(current.id, true);
        current = current.parentElement?.closest(".test, .card");
    }
}

function resetAllBlocks(){
    getAll(".test-content").forEach(c => toggleClass(c, "active", false));
    getAll(".test-header").forEach(h => toggleClass(h, "expanded", false));
    localStorage.removeItem("expandedTests");
}

// ===================== HASH HANDLING =====================
window.addEventListener("load", () => {
    restoreExpandedState();
    const hash = location.hash.slice(1);
    if(hash){
        const el = getElById(hash);
        if(el){
            el.classList.add("highlight");
            el.scrollIntoView({behavior:"smooth"});
            expandTestAndParents(el);
        }
    }
});

window.addEventListener("popstate", event => {
    restoreExpandedState();
    const id = event.state?.openedId;
    if(id){
        const el = getElById(id);
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

const modal          = getElById('attachmentModal');
const titleEl        = getElById('modalTitle');
const image          = getElById('modalImage');
const imageContainer = getElById('imageContainer');
const textPreview    = getElById('modalText');
const pdfContainer   = getElById('modalPDF');
const download       = getElById('modalDownload');

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
                if (textPreview) {
                    textPreview.textContent = text;
                    textPreview.style.display = 'block';
                }
            })
            .catch(() => {
                if (textPreview) {
                    textPreview.textContent = '[Ошибка загрузки текста]';
                    textPreview.style.display = 'block';
                }
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

// Zoom + Drag
if (imageContainer) {
    imageContainer.addEventListener('wheel', (e) => {
        e.preventDefault();
        scale = Math.min(Math.max(scale - e.deltaY * 0.001, 0.5), 5);
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
//  THEME
// ======================================================

const root = document.documentElement;
const themeToggle = getElById("themeToggle");
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


// ======================================================
//  HELPER FUNCTIONS
// ======================================================

function getElById(id) {
    return document.getElementById(id);
}

function getAll(selector, parent = document) {
    return Array.from(parent.querySelectorAll(selector));
}

function getElBySelector(selector, parent = document) {
    return parent.querySelector(selector);
}

function toggleClass(el, className, force) {
    if (!el) return;
    el.classList.toggle(className, force);
}

function saveToStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function loadFromStorage(key, defaultValue = null) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : defaultValue;
}