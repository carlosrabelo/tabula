import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/natureza_participacao.csv';

export async function renderNaturezaChart() {
  const canvas = document.getElementById('chartNatureza');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('natureza_participacao.csv');
    renderPlaceholder(canvas, 'Sem dados de natureza de participação no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('natureza_participacao.csv');
    renderPlaceholder(canvas, 'Sem registros de natureza de participação para exibir.');
    return;
  }

  const labels = rows
    .map((row) => row.Natureza_Participacao || row.natureza_participacao)
    .filter((value) => value && value.length > 0);
  const values = rows.map((row) => Number(row.qtd || row.Qtd || 0));
  const total = values.reduce((sum, value) => sum + value, 0);

  if (!labels.length) {
    renderPlaceholder(canvas, 'Natureza de Participação não informada na planilha.');
    return;
  }

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
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
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
        y: {
          title: { display: true, text: 'Natureza de Participação' },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label(context) {
              const value = context.parsed.x ?? 0;
              const pct = percentage(value, total);
              return `${numberFormatter.format(value)} alunos (${percentFormatter.format(pct)}%)`;
            },
          },
        },
      },
    },
  });
}
