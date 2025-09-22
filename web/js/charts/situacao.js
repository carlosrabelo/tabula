import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getStatusColor,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/alunos_por_situacao.csv';

export async function renderSituacaoChart() {
  const canvas = document.getElementById('chartSituacao');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('alunos_por_situacao.csv');
    renderPlaceholder(canvas, 'Sem dados de situação acadêmica no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('alunos_por_situacao.csv');
    renderPlaceholder(canvas, 'Sem registros de situação para exibir.');
    return;
  }

  const items = rows
    .map((row) => ({
      label: row.Situacao || row.situacao || 'Não informado',
      value: Number(row.qtd || row.Qtd || 0) || 0,
    }))
    .sort((a, b) => b.value - a.value);

  const total = items.reduce((sum, item) => sum + item.value, 0);
  const labels = items.map((item) => item.label);
  const values = items.map((item) => item.value);

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Alunos',
          data: values,
          backgroundColor: labels.map((label, index) => getStatusColor(label, index)),
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
        y: { title: { display: true, text: 'Situação Acadêmica' } },
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
