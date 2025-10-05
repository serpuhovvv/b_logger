// ======================================================
//  Filters + Sorting (постоянное хранение состояния)
// ======================================================

document.addEventListener('DOMContentLoaded', initFilters);

function initFilters() {
    const searchInput  = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const moduleFilter = document.getElementById('moduleFilter');
    const resetBtn     = document.getElementById('reset-filters');
    const sortBtns     = Array.from(document.querySelectorAll('.sort-btn'));
    const filterBtns   = Array.from(document.querySelectorAll('.filter-btn'));

    // --- Восстановление состояния из localStorage ---
    // Сортировка
    const savedSort = localStorage.getItem('selectedSort') || 'name_asc';
    sortBtns.forEach(b => b.classList.toggle('active', b.dataset.sort === savedSort));

    // Активные фильтры по статусам
    try {
        const savedFilters = JSON.parse(localStorage.getItem('activeFilters') || '[]');
        if (Array.isArray(savedFilters) && savedFilters.length) {
            filterBtns.forEach(b => b.classList.toggle('active', savedFilters.includes(b.dataset.filter)));
        }
    } catch (e) {
        // ignore parse errors
    }

    // --- Слушатели для элементов управления ---
    searchInput?.addEventListener('input', filterTests);
    statusFilter?.addEventListener('change', filterTests);
    moduleFilter?.addEventListener('change', filterTests);
    searchInput?.addEventListener('keydown', e => { if (e.key === 'Escape') { searchInput.value = ''; filterTests(); } });

    // filter buttons (toggle + save)
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('active');
            // сохраняем активные фильтры
            const active = filterBtns.filter(b => b.classList.contains('active'))
                                     .map(b => b.dataset.filter)
                                     .filter(Boolean);
            if (active.length) localStorage.setItem('activeFilters', JSON.stringify(active));
            else localStorage.removeItem('activeFilters');
            filterTests();
        });
    });

    // sort buttons (one active)
    sortBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // включаем только эту кнопку
            sortBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // сохраняем выбранную сортировку
            if (btn.dataset.sort) localStorage.setItem('selectedSort', btn.dataset.sort);
            filterTests();
        });
    });

    // reset
    resetBtn?.addEventListener('click', () => {
        // очистка UI
        if (searchInput) searchInput.value = '';
        clearSelect(statusFilter);
        clearSelect(moduleFilter);

        filterBtns.forEach(b => b.classList.remove('active'));
        document.querySelector('.filter-btn[data-filter="all"]')?.classList.add('active');

        sortBtns.forEach(b => b.classList.remove('active'));
        // установим дефолтную сортировку A–Z
        const defaultSort = 'name_asc';
        const defaultBtn = document.querySelector(`.sort-btn[data-sort="${defaultSort}"]`);
        if (defaultBtn) defaultBtn.classList.add('active');

        // очистка localStorage
        localStorage.removeItem('activeFilters');
        localStorage.setItem('selectedSort', defaultSort);

        filterTests();
    });

    // Первичный прогон (восстановленные состояния уже применены)
    filterTests();
}

/* ----------------- HELPERS ----------------- */
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

function normalizeStatus(s) {
    return (s ?? '').toString().trim().toUpperCase();
}

function matchesFilters(nameLC, statusRaw, moduleName, filters) {
    const statusU = normalizeStatus(statusRaw);
    if (filters.search && !nameLC.includes(filters.search)) return false;
    if (filters.status.length && !filters.status.includes(statusU)) return false;
    if (filters.module.length && !filters.module.includes(moduleName)) return false;
    if (filters.buttonStatuses.length && !filters.buttonStatuses.includes(statusU.toLowerCase())) return false;
    return true;
}

/* ----------------- СОРТИРОВКА ----------------- */
function getSortOptions() {
    const activeBtn = document.querySelector('.sort-btn.active');
    const defaultDs = 'name_asc';
    const ds = (activeBtn?.dataset?.sort) || defaultDs;
    const [field, order] = ds.split('_');
    return { field: field || 'name', order: order === 'desc' ? 'desc' : 'asc' };
}

function compareTests(a, b, field, order = 'asc') {
    // status priority: меньший = выше в списке при order='asc'
    const statusOrder = { FAILED: 1, BROKEN: 2, SKIPPED: 3, PASSED: 4 };

    let A, B;
    switch (field) {
        case 'name':
            A = (a.dataset.test || '').toLowerCase();
            B = (b.dataset.test || '').toLowerCase();
            break;
        case 'duration':
            A = parseFloat(a.dataset.duration || '0') || 0;
            B = parseFloat(b.dataset.duration || '0') || 0;
            break;
        case 'status':
            A = statusOrder[(a.dataset.status || '').toUpperCase()] || 99;
            B = statusOrder[(b.dataset.status || '').toUpperCase()] || 99;
            break;
        default:
            A = (a.dataset.test || '').toLowerCase();
            B = (b.dataset.test || '').toLowerCase();
    }

    if (A < B) return order === 'asc' ? -1 : 1;
    if (A > B) return order === 'asc' ? 1 : -1;
    return 0;
}

/* ----------------- ФИЛЬТРАЦИЯ + СОРТИРОВКА ----------------- */
function filterTests() {
    const search = (document.getElementById('searchInput')?.value || '').toLowerCase().trim();
    const statusSelected = getSelectedValues(document.getElementById('statusFilter')).map(v => v.toUpperCase());
    const moduleSelected = getSelectedValues(document.getElementById('moduleFilter'));
    const activeButtons = Array.from(document.querySelectorAll('.filter-btn.active'))
        .map(b => (b.dataset.filter || '').toLowerCase().trim())
        .filter(f => f && f !== 'all');

    const { field: sortField, order: sortOrder } = getSortOptions();
    const filters = { search, status: statusSelected, module: moduleSelected, buttonStatuses: activeButtons };

    const modules = document.querySelectorAll('.module');
    let modulesVisible = 0;

    modules.forEach(moduleEl => {
        const moduleName = moduleEl.dataset.module;
        const container = moduleEl.querySelector('.tests-list');
        if (!container) return;

        // Топ-уровневые тесты (не захватываем .test-sub)
        const topTests = Array.from(container.querySelectorAll(':scope > .test'));

        // 1) Сортируем topTests (по всем, даже скрытым)
        if (sortField) {
            topTests.sort((a, b) => compareTests(a, b, sortField, sortOrder));
            topTests.forEach(t => container.appendChild(t));
        }

        // 2) Для каждого test-multi: сортируем его под-тесты (если есть)
        topTests.forEach(test => {
            if (test.classList.contains('test-multi')) {
                const subContainer = test.querySelector(':scope > .test-content');
                if (subContainer) {
                    const subTests = Array.from(subContainer.querySelectorAll(':scope > .test-sub'));
                    if (sortField) {
                        subTests.sort((a, b) => compareTests(a, b, sortField, sortOrder));
                        subTests.forEach(st => subContainer.appendChild(st));
                    }
                }
            }
        });

        // 3) Применяем фильтры (показываем/скрываем)
        let moduleHasVisible = false;

        topTests.forEach(test => {
            const isGroup = test.classList.contains('test-multi');
            const testName = (test.dataset.test || '').toLowerCase();
            let visible = false;

            if (isGroup) {
                const subContainer = test.querySelector(':scope > .test-content');
                const subTests = subContainer ? Array.from(subContainer.querySelectorAll(':scope > .test-sub')) : [];

                let subVisible = 0;
                subTests.forEach(sub => {
                    const subName = (sub.dataset.test || '').toLowerCase();
                    const subStatus = sub.dataset.status;
                    const show = matchesFilters(subName, subStatus, moduleName, filters);
                    sub.style.display = show ? 'block' : 'none';
                    if (show) subVisible++;
                });

                visible = subVisible > 0;
            } else {
                const testStatus = test.dataset.status;
                visible = matchesFilters(testName, testStatus, moduleName, filters);
            }

            test.style.display = visible ? 'block' : 'none';
            if (visible) moduleHasVisible = true;
        });

        moduleEl.style.display = moduleHasVisible ? 'block' : 'none';
        if (moduleHasVisible) modulesVisible++;
    });

    // no-results
    let noResults = document.getElementById('noResults');
    if (modulesVisible === 0) {
        if (!noResults) {
            noResults = document.createElement('div');
            noResults.id = 'noResults';
            noResults.className = 'no-results';
            noResults.innerHTML = '<i class="fas fa-search"></i><br>No tests match your filters';
            document.querySelector('.main-content')?.appendChild(noResults);
        }
    } else {
        noResults?.remove();
    }
}


// ======================================================
//  UI-Toggles
// ======================================================

function toggleBlock(header) {
    const content = header.nextElementSibling;
    if (!content) return;
    content.classList.toggle('active');
    header.classList.toggle('expanded');
}

function toggleStacktrace(el) {
    el.classList.toggle("expanded");
    el.nextElementSibling?.classList.toggle("active");
}

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


// ======================================================
//  Navigation / Hash
// ======================================================

function toggleTestAndHash(header) {
    const el = header.closest(".test, .card");
    if (!el || !el.id) return;

    const content = header.nextElementSibling;
    const isOpening = !content.classList.contains("active");

    toggleBlock(header);

    history.pushState(
        isOpening ? { openedId: el.id } : {},
        "",
        isOpening ? `#${el.id}` : location.pathname + location.search
    );
}

function expandTestAndParents(el) {
    if (!el) return;
    let current = el;
    while (current) {
        const header = current.querySelector(":scope > .test-header, :scope > .test-header-multi, :scope > .header");
        const content = current.querySelector(":scope > .test-content, :scope > .content");
        header?.classList.add("expanded");
        content?.classList.add("active");
        current = current.parentElement?.closest(".test, .card");
    }
}

function resetAllBlocks() {
    document.querySelectorAll(".test-content, .content").forEach(c => c.classList.remove("active"));
    document.querySelectorAll(".test-header, .test-header-multi").forEach(h => h.classList.remove("expanded"));
}

window.addEventListener("load", () => {
    const hash = location.hash.slice(1);
    if (!hash) return;
    const el = document.getElementById(hash);
    if (el) {
        el.classList.add("highlight");
        el.scrollIntoView({ behavior: "smooth" });
        expandTestAndParents(el);
    }
});

window.addEventListener("popstate", event => {
    const id = event.state?.openedId;
    if (!id) return;
    const el = document.getElementById(id);
    if (el) {
        el.classList.add("highlight");
        el.scrollIntoView({ behavior: "smooth" });
        expandTestAndParents(el);
    }
});


// ======================================================
//  Init
// ======================================================

document.addEventListener('DOMContentLoaded', initFilters);
