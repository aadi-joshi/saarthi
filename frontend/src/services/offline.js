/**
 * Offline Storage Service using IndexedDB
 * Enables offline bill payment queue
 */
import { openDB } from 'idb';

const DB_NAME = 'suvidha-offline';
const DB_VERSION = 1;

// Initialize IndexedDB
const dbPromise = openDB(DB_NAME, DB_VERSION, {
  upgrade(db) {
    // Pending transactions store
    if (!db.objectStoreNames.contains('pending_transactions')) {
      const store = db.createObjectStore('pending_transactions', {
        keyPath: 'id',
        autoIncrement: true,
      });
      store.createIndex('status', 'status');
      store.createIndex('created_at', 'created_at');
    }

    // Cached bills store
    if (!db.objectStoreNames.contains('cached_bills')) {
      const store = db.createObjectStore('cached_bills', {
        keyPath: 'id',
      });
      store.createIndex('user_id', 'user_id');
    }

    // User data store
    if (!db.objectStoreNames.contains('user_data')) {
      db.createObjectStore('user_data', {
        keyPath: 'key',
      });
    }
  },
});

// Pending Transactions
export const offlineTransactions = {
  // Add a new pending transaction
  async add(transaction) {
    const db = await dbPromise;
    const data = {
      ...transaction,
      status: 'pending',
      created_at: new Date().toISOString(),
      sync_attempts: 0,
    };
    const id = await db.add('pending_transactions', data);
    return { id, ...data };
  },

  // Get all pending transactions
  async getAll() {
    const db = await dbPromise;
    return db.getAllFromIndex('pending_transactions', 'status', 'pending');
  },

  // Mark transaction as synced
  async markSynced(id, serverResponse) {
    const db = await dbPromise;
    const tx = await db.get('pending_transactions', id);
    if (tx) {
      tx.status = 'synced';
      tx.synced_at = new Date().toISOString();
      tx.server_response = serverResponse;
      await db.put('pending_transactions', tx);
    }
  },

  // Mark transaction as failed
  async markFailed(id, error) {
    const db = await dbPromise;
    const tx = await db.get('pending_transactions', id);
    if (tx) {
      tx.status = 'failed';
      tx.error = error;
      tx.sync_attempts += 1;
      await db.put('pending_transactions', tx);
    }
  },

  // Delete old synced transactions (cleanup)
  async cleanup(daysOld = 7) {
    const db = await dbPromise;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - daysOld);
    
    const all = await db.getAll('pending_transactions');
    for (const tx of all) {
      if (tx.status === 'synced' && new Date(tx.synced_at) < cutoff) {
        await db.delete('pending_transactions', tx.id);
      }
    }
  },
};

// Cached Bills
export const cachedBills = {
  async cache(bills) {
    const db = await dbPromise;
    const tx = db.transaction('cached_bills', 'readwrite');
    for (const bill of bills) {
      await tx.store.put(bill);
    }
    await tx.done;
  },

  async getAll() {
    const db = await dbPromise;
    return db.getAll('cached_bills');
  },

  async get(id) {
    const db = await dbPromise;
    return db.get('cached_bills', id);
  },

  async clear() {
    const db = await dbPromise;
    await db.clear('cached_bills');
  },
};

// User Data
export const userData = {
  async set(key, value) {
    const db = await dbPromise;
    await db.put('user_data', { key, value });
  },

  async get(key) {
    const db = await dbPromise;
    const result = await db.get('user_data', key);
    return result?.value;
  },

  async delete(key) {
    const db = await dbPromise;
    await db.delete('user_data', key);
  },
};

// Sync pending transactions when online
export async function syncPendingTransactions() {
  if (!navigator.onLine) return { synced: 0, failed: 0 };

  const pending = await offlineTransactions.getAll();
  let synced = 0;
  let failed = 0;

  for (const tx of pending) {
    try {
      const response = await fetch('/api/v1/bills/pay', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(tx.data),
      });

      if (response.ok) {
        const result = await response.json();
        await offlineTransactions.markSynced(tx.id, result);
        synced++;
      } else {
        const error = await response.text();
        await offlineTransactions.markFailed(tx.id, error);
        failed++;
      }
    } catch (error) {
      await offlineTransactions.markFailed(tx.id, error.message);
      failed++;
    }
  }

  return { synced, failed };
}

// Register for online event
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    syncPendingTransactions().then(({ synced, failed }) => {
      if (synced > 0) {
        console.log(`Synced ${synced} offline transactions`);
      }
    });
  });
}
