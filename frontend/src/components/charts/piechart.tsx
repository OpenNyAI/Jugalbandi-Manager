import "./chart.css";

import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";

import { Pie } from "react-chartjs-2";
import React from "react";

ChartJS.register(ArcElement, Tooltip, Legend);

interface IChartProps {
  title: string;
}

export const data = {
  labels: ["Telegram Users", "Whatsapp Users"],
  datasets: [
    {
      label: "% of users",
      data: [27, 73],
      backgroundColor: ["rgb(100, 219, 254)", "rgb(144, 232, 142)"],
      borderWidth: 0,
    },
  ],
};

export const PieChart: React.FunctionComponent<IChartProps> = (props) => {
  const { title } = props;

  return (
    <div className="pieChart">
      <Pie data={data} />
    </div>
  );
};
