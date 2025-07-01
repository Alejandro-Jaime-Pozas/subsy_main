import React, { useState, useEffect, useCallback } from "react";
import { usePlaidLink } from "react-plaid-link";
import "./App.scss";
import { safeParse } from "./utils/LocalStorageUtils"
import { toTitleCase } from "./utils/PrettyPrintUtils"

function App(props) {
  const [token, setToken] = useState(null);
  // set the balance and transaction data to the data retreived from local storage, if it exists
  // WILL LATER PROB NEED TO RESOLVE IF JSON PARSE STILL NOT WORKING IN safeParse fn
  const [data, setData] = useState(safeParse('balance'));
  const [allTransactions, setAllTransactions] = useState(safeParse('all_transactions'));
  // const [latestTransactions, setLatestTransactions] = useState(safeParse('latest_transactions'));
  const [loading, setLoading] = useState(false);

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

  // Handle successful Plaid Link flow
  const onSuccess = useCallback(async (publicToken) => {
    setLoading(true);
    const response = await fetch("/api/exchange_public_token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ public_token: publicToken }),
    });
    const data = await response.json();
    console.log(data);
    // TODO later automatically create all objects required once we have ingested all transaction history
    // await getBalance();
    // await getAllTransactions();
  }, []);

  // Fetch balance data
  const getBalance = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/balance/", {});
    const data = await response.json();
    setData(data);
    localStorage.setItem("balance", JSON.stringify(data));
    setLoading(false);
    console.log(data)
  }, [setData, setLoading]);

  // Fetch all transaction data
  const getAllTransactions = useCallback(async () => {
    setLoading(true);
    const response = await fetch("/api/get_all_transactions/", {});
    const data = await response.json();
    setAllTransactions(data.all_transactions);
    localStorage.setItem("all_transactions", JSON.stringify(data.all_transactions));
    setLoading(false);
    console.log('Hello World from getAllTransactions');
    console.log(data);
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
    // console.log(allTransactions);
    // console.log(latestTransactions);
    if (token == null) {
      console.log('No token, will create one now.')
      createLinkToken();
    }
    if (isOauth && ready) {
      open();
    }
  }, [token, isOauth, ready, open]);


  return (
    <div>
      <button onClick={() => open()
        } disabled={!ready}>
        <strong>Link account</strong>
      </button>
      <button onClick={() => getBalance()
        } disabled={!ready}>
        <strong>Get Balance</strong>
      </button>
      <button onClick={() => getAllTransactions()
        } disabled={!ready}>
        <strong>Get All Transactions</strong>
      </button>
      !!!ALL PRETTY TRANSACTIONS!!!
      {/* if transaction data has been retreived successfully, show pretty data */}
      {!loading &&
        // MAP ALL TRANSACTIONS
        allTransactions != null &&
        allTransactions.added.map((entry, i) => (
          <div className="transactions-plaid row " key={i}>
            {entry.logo_url ?
              <img className='tr-image img-fluid col-1 rounded-circle ' src={entry.logo_url} alt="" />
            :
              <img className='tr-image img-fluid col-1 rounded-circle ' src={entry.personal_finance_category_icon_url} alt="" />
            }
            {entry.merchant_name ?
              <div className="tr-data div col">{entry.merchant_name}</div>
            :
              <div className="tr-data div col">{entry.name}</div>
            }
            <div className="tr-data div col-1">{entry.amount}</div>
            <div className="tr-data div col">{entry.date}</div>
            <div className="tr-data div col-5 ">{toTitleCase(entry.personal_finance_category.detailed)}</div>
          </div>
        )
      )}
      {/* if balance data has been retreived successfully, show data */}
      !!!BALANCE!!!
      {!loading &&
        data != null &&
        Object.entries(data).map((entry, i) => (
          <pre key={i}>
            <code>{JSON.stringify(entry[1], null, 2)}</code>
          </pre>
        )
      )}
      !!!ALL TRANSACTIONS!!!
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
