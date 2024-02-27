import "./chart.css";

import { ArcElement, Chart as ChartJS, Legend, Tooltip } from "chart.js";

import { Doughnut } from "react-chartjs-2";
import React from "react";

ChartJS.register(ArcElement, Tooltip, Legend);

interface IChartProps {
  title: string;
}

export const data = {
  labels: ["Automation", "Coach response", "Api", "Thread", "System", "Other"],
  datasets: [
    {
      label: "% of responses",
      data: [38, 22.8, 16.5, 11.3, 6.3, 5],
      backgroundColor: [
        "rgb(251,217,13)",
        "rgb(255,112,78)",
        "rgb(100,219,254)",
        "rgb(144,232,142)",
        "rgb(254,157,44)",
        "rgb(212,181,255)",
      ],
      borderWidth: 0,
    },
  ],
};

export const DoughnutChart: React.FunctionComponent<IChartProps> = (props) => {
  const { title } = props;

  return (
    <div className="doughnutChart">
      <Doughnut data={data} />
    </div>
  );
};
