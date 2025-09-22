import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/necessidades_especiais.csv';

export async function renderNecessidadesChart() {
  const canvas = document.getElementById('chartNecessidades');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('necessidades_especiais.csv');
    renderPlaceholder(canvas, 'Sem dados de necessidades especiais no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('necessidades_especiais.csv');
    renderPlaceholder(canvas, 'Sem registros de necessidades especiais para exibir.');
    return;
  }

  const labels = rows
    .map((row) => row.Tem_NE || row.tem_ne || 'Não informado')
    .filter((value) => value && value.length > 0);
  const values = rows.map((row) => Number(row.qtd || row.Qtd || 0) || 0);
  const total = values.reduce((sum, value) => sum + value, 0);

  if (!labels.length) {
    renderPlaceholder(canvas, 'Sem informação sobre necessidades especiais.');
    return;
  }

  new Chart(canvas.getContext('2d'), {
    type: 'pie',
    data: {
      labels,
      datasets: [
        {
          label: 'Alunos',
          data: values,
          backgroundColor: labels.map((_, index) => getColorByIndex(index)),
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed || 0;
              const pct = percentage(value, total);
              return `${context.label}: ${numberFormatter.format(value)} (${percentFormatter.format(pct)}%)`;
            },
          },
        },
      },
    },
  });
}
