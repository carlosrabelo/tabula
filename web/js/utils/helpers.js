export const numberFormatter = new Intl.NumberFormat('pt-BR');
export const percentFormatter = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
});

const STATUS_COLORS = {
  'Concluído': '#2e7d32',
  'Ativo': '#1976d2',
  'Trancado': '#f9a825',
  'Evasão/Cancelado': '#c62828',
  'Outros': '#6d4c41',
};

const BASE_PALETTE = [
  '#1976d2',
  '#2e7d32',
  '#c62828',
  '#f9a825',
  '#6d4c41',
  '#00838f',
  '#6a1b9a',
  '#ef6c00',
  '#455a64',
  '#7cb342',
];

export function getStatusColor(status, index = 0) {
  return STATUS_COLORS[status] || getColorByIndex(index);
}

export function getColorByIndex(index) {
  return BASE_PALETTE[index % BASE_PALETTE.length];
}

export function safeNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function percentage(part, total) {
  if (!total) {
    return 0;
  }
  return (part / total) * 100;
}

export function datasetMissing(name) {
  console.warn(`dataset ausente: ${name}`);
}

export function renderPlaceholder(canvas, message) {
  if (!canvas) {
    return;
  }
  const wrapper = canvas.closest('.chart-wrapper');
  if (!wrapper) {
    return;
  }
  wrapper.innerHTML = `<div class="chart-placeholder">${message}</div>`;
}
