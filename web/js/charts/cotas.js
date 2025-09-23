import { loadCSV } from '../utils/csv.js';
import {
  datasetMissing,
  getColorByIndex,
  numberFormatter,
  percentFormatter,
  percentage,
  renderPlaceholder,
} from '../utils/helpers.js';

const DATASET_PATH = 'datasets/cotas.csv';

export async function renderCotasChart() {
  const canvas = document.getElementById('chartCotas');
  if (!canvas) {
    return;
  }

  let rows;
  try {
    rows = await loadCSV(DATASET_PATH);
  } catch (error) {
    datasetMissing('cotas.csv');
    renderPlaceholder(canvas, 'Sem dados de cotas no arquivo mestre.');
    return;
  }

  if (!rows.length) {
    datasetMissing('cotas.csv');
    renderPlaceholder(canvas, 'Sem registros de cotas para exibir.');
    return;
  }

  const categorias = [...new Set(rows.map((row) => row.Categoria || 'Não informado'))];
  const tiposCota = [...new Set(rows.map((row) => row.Tipo_Cota))];

  const datasets = tiposCota.map((tipo, index) => {
    const data = categorias.map((cat) => {
      const row = rows.find((r) => r.Tipo_Cota === tipo && r.Categoria === cat);
      return row ? Number(row.qtd) : 0;
    });
    return {
      label: tipo,
      data: data,
      backgroundColor: getColorByIndex(index),
      borderWidth: 1,
    };
  });

  const total = datasets.flatMap((ds) => ds.data).reduce((sum, value) => sum + value, 0);

  new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
      labels: categorias,
      datasets: datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: { display: true, text: 'Categoria da Cota' },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: 'Quantidade de Alunos' },
          ticks: { callback: (value) => numberFormatter.format(value) },
        },
      },
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          callbacks: {
            label(context) {
              const label = context.dataset.label || '';
              const value = context.parsed.y ?? 0;
              const pct = percentage(value, total);
              return `${label}: ${numberFormatter.format(
                value
              )} alunos (${percentFormatter.format(pct)}%)`;
            },
          },
        },
      },
    },
  });
}
