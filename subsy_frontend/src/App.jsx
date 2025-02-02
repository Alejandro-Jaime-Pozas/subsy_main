import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import "./App.scss";

function App(props) {
  const [token, setToken] = useState(null);
  // set the balance and transaction data to the data retreived from local storage, if it exists
  const [data, setData] = useState(JSON.parse(localStorage.getItem("balance")) || null);
  const [allTransactions, setAllTransactions] = useState(JSON.parse(localStorage.getItem("all_transactions")) || null);
  const [latestTransactions, setLatestTransactions] = useState(JSON.parse(localStorage.getItem("latest_transactions")) || null);
  const [loading, setLoading] = useState(false);

  const onSuccess = useCallback(async (publicToken) => {
    setLoading(true);
    await fetch("/api/exchange_public_token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ public_token: publicToken }),
    });
    await getLatestTransactions();
    await getAllTransactions();
    await getBalance();
  }, []);

  // Creates a Link token
  const createLinkToken = useCallback(async () => {
    // For OAuth, use previously generated Link token
    if (window.location.href.includes("?oauth_state_id=")) {
      console.log('OAuth is included in the url, will proceed with OAuth process for creating link token.')
      const linkToken = localStorage.getItem('link_token');
      setToken(linkToken);
    } else {
      console.log('Fetching link token from backend, which fetches from plaid.');
      const response = await fetch("/api/create_link_token/", {});
      const data = await response.json();
      setToken(data.link_token);
      localStorage.setItem("link_token", data.link_token);
      console.log(`Link token successfully fetched and created: ${data.link_token}`);
    }
  }, [setToken]);

  // Fetch balance data
  const getBalance = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/balance/", {});
    const data = await response.json();
    setData(data);
    localStorage.setItem("balance", JSON.stringify(data));
    setLoading(false);
    // console.log(data)
  }, [setData, setLoading]);

  // Fetch latest transaction data
  const getLatestTransactions = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/get_latest_transactions/", {});
    const data = await response.json();
    setLatestTransactions(data.latest_transactions);
    localStorage.setItem("latest_transactions", JSON.stringify(data.latest_transactions));
    setLoading(false);
    console.log(data);
  }, [setLatestTransactions, setLoading]);

  // Fetch all transaction data
  const getAllTransactions = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/get_all_transactions/", {});
    const data = await response.json();
    setAllTransactions(data.all_transactions);
    localStorage.setItem("all_transactions", JSON.stringify(data.all_transactions));
    setLoading(false);
    // console.log(data);
  }, [setAllTransactions, setLoading]);

  let isOauth = false;

  const config = {
    token,
    onSuccess,
  };

  // For OAuth, configure the received redirect URI
  if (window.location.href.includes("?oauth_state_id=")) {
    config.receivedRedirectUri = window.location.href;
    isOauth = true;
  }
  const { open, ready } = usePlaidLink(config);  // why is this function never called anywhere else?

  // need to understand this below
  useEffect(() => {
    if (token == null) {
      console.log('No token, will create one now.')
      createLinkToken();
    }
    if (isOauth && ready) {
      open();
    }
  }, [token, isOauth, ready, open]);

  // Function to transform uppercase snake_case to Title Case with spaces
  function toTitleCase(str) {
    return str
      .split('_')                          // Split by underscores
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter of each word
      .join(' ');                           // Join words with a space
  }

  return (
    <div>
      <button onClick={() => open()
        } disabled={!ready}>
        <strong>Link account</strong>
      </button>
      {/* if transaction data has been retreived successfully, show data */}
      {/* try displaying the transactions as I want them.
          merchant logo
          merchant name
          amount
          date
        (if there is some sort of description about the product purchase, ideal) */}
      {!loading &&
        latestTransactions != null &&
        latestTransactions.map((entry, i) => (
          <div className="transactions-plaid row " key={i}>
            {entry.logo_url ?
              <img className='tr-image img-fluid col-1 rounded-circle ' src={entry.logo_url} alt="" />
            :
              <img className='tr-image img-fluid col-1 rounded-circle ' src={entry.personal_finance_category_icon_url} alt="" />
            }
            {/* <div className="tr-data div col">{entry.name}</div> */}
            <div className="tr-data div col">{entry.merchant_name}</div>
            <div className="tr-data div col-1">{entry.amount}</div>
            <div className="tr-data div col">{entry.date}</div>
            <div className="tr-data div col-5 ">{toTitleCase(entry.personal_finance_category.detailed)}</div>
          </div>
        )
      )}
      {/* if balance data has been retreived successfully, show data */}
      {!loading &&
        data != null &&
        Object.entries(data).map((entry, i) => (
          <pre key={i}>
            <code>{JSON.stringify(entry[1], null, 2)}</code>
          </pre>
        )
      )}
      TRANSACTIONS!!!
      {/* show latest transactions json */}
      {/* {!loading &&
        latestTransactions != null &&
        Object.entries(latestTransactions).map((entry, i) => (
          <pre key={i}>
            <code>{JSON.stringify(entry[1], null, 2)}</code>
          </pre>
        )
      )} */}
      {/* show all transactions json */}
      {!loading &&
        allTransactions != null &&
        Object.entries(allTransactions).map((entry, i) => (
          <pre key={i}>
            <code>{JSON.stringify(entry[1], null, 2)}</code>
          </pre>
        )
      )}
    </div>
  );
}

export default App;
