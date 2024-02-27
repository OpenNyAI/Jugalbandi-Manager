import "./chart.css";

import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from "chart.js";

import { Bar } from "react-chartjs-2";
import React from "react";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface IChartProps {
  title: string;
  chartData: [];
  labels: [];
}

export const options = {
  plugins: {
    title: {
      display: false,
      text: "",
    },
  },
  responsive: true,
  scales: {
    x: {
      stacked: true,
    },
    y: {
      stacked: true,
    },
  },
};

export const BarChart: React.FunctionComponent<IChartProps> = (props) => {
  const { labels, chartData } = props;

  const usersData = {
    labels: labels,
    datasets: chartData,
  };

  return (
    <div className="barChart">
      <Bar options={options} data={usersData} />
    </div>
  );
};
