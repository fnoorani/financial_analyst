<html>
<head>
<title>{{ticker_info['longNamee']}}</title>

<style>
.item-a {
  grid-area: logo;
  border-bottom: 1px solid black;
}

.item-b {
  grid-area: header;
  border-bottom: 1px solid black;
  font-size: 36px;
  font-weight: bold;
  display: flex;
}

.item-b span {
  align-self: flex-end;
}

.item-c {
  grid-area: main;
  border: 1px solid dashed;
}

.item-c p {
  font-style: italic;
  color: teal;
}

.item-d {
  grid-area: sidebar;
  font-size: 14px;
}
.item-e {
  grid-area: footer;
  border-top: 1px solid black;
}

.container {
  display: grid;
  grid-template-columns: 195px 450px 450px 150px;
  grid-template-rows: auto;
  justify-content: center;
  align-content: center;
  grid-template-areas:
    "logo header header header"
    "sidebar main main main"
    "footer footer footer footer";
}
</style>

</head>

<body>

<div class="container">

  <div class="item-a"> <img src="{{ticker_info['logo_url']}}"/> </div>

  <div class="item-b"> <span class="title">{{ticker_info['symbol']}} - {{ticker_info['longName']}} - {{ticker_info['sector']}} - {{ticker_info['industry']}}</span></div>

  <div class="item-c">
    <p>{{ticker_info['longBusinessSummary']}}</p>
    <img src="http://localhost:5000/volatility/{{ticker_info['symbol']}}"/>
    <img src="http://localhost:5000/volatility/long/{{ticker_info['symbol']}}"/>
  </div>

  <div class="item-d">
    <ui>
      <li>Forward PE: {{ticker_info['forwardPE']}}</li>
      <li>Sector: {{ticker_info['sector']}}<l/i>
      <li>fullTimeEmployees: {{ticker_info['fullTimeEmployees']}}</li>
      <li>companyOfficers: {{ticker_info['companyOfficers']}}</li>
      <li>website: <a href="{{ticker_info['website']}}">company website</a> </li>
      <li>profitMargins: {{ticker_info['profitMargins']}}</li>
      <li>forwardEps: {{ticker_info['forwardEps']}}</li>
      <li>revenueQuarterlyGrowth: {{ticker_info['revenueQuarterlyGrowth']}}</li>
    </ul>
  </div>

  <div class="item-e"> footer </footer>

</div>

</body>

</html>