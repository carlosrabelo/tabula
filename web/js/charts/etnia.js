import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/etnia_raca.csv';

export async function renderEtniaChart() {
  const canvas = document.getElementById('chartEtnia');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('etnia_raca.csv');
    renderPlaceholder(canvas, 'Sem dados de etnia/raça no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('etnia_raca.csv');
    renderPlaceholder(canvas, 'Sem registros de etnia/raça para exibir.');
    return;
  }

  const labels = rows
    .map((row) => row.Etnia_Raca || row.etnia_raca || 'Não informado')
    .filter((value) => value && value.length > 0);
  const values = rows.map((row) => Number(row.qtd || row.Qtd || 0) || 0);
  const total = values.reduce((sum, value) => sum + value, 0);

  if (!labels.length) {
    renderPlaceholder(canvas, 'Categorias de etnia não informadas.');
    return;
  }

  new Chart(canvas.getContext('2d'), {
    type: 'doughnut',
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
