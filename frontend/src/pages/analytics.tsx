import {
  axisLabels,
  creditsData,
  msgData,
  usersData,
} from "../components/charts/chartData";

import { BarChart } from "../components/charts/barchart";
import { DoughnutChart } from "../components/charts/doughnutchart";
import { PieChart } from "../components/charts/piechart";
import { useLocation } from "react-router-dom";

function Analytics() {
  const location = useLocation();
  const { from } = location.state;

  return (
    <div className="chartPage">
      <div className="chartMain">
        <h3>Active Users</h3>
        <div className="chartComponent">
          <BarChart
            title="Active Users"
            labels={axisLabels}
            chartData={usersData}
          />
          <PieChart title="Active Users" />
        </div>
      </div>

      <div className="chartGrid">
        <div className="chartLeft">
          <div className="chartMain">
            <h3>Engagement</h3>
            <div className="chartComponent">
              <BarChart
                title="Active Users"
                labels={axisLabels}
                chartData={msgData}
              />
            </div>
          </div>
          <div className="chartMain">
            <h3>Credits</h3>
            <div className="chartComponent">
              <BarChart
                title="Active Users"
                labels={axisLabels}
                chartData={creditsData}
              />
            </div>
          </div>
        </div>
        <div className="chartRight">
          <div className="chartMain">
            <h3>Response Type</h3>
            <div className="chartComponent">
              <DoughnutChart />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;
