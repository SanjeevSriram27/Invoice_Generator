'use client';

import { useState } from 'react';
import type { InvoiceItem } from '@/types/invoice';

interface AddItemFormProps {
  onAdd: (item: InvoiceItem) => void;
}

export default function AddItemForm({ onAdd }: AddItemFormProps) {
  const [item, setItem] = useState<InvoiceItem>({
    description: '',
    hsn_sac: '',
    quantity: 1,
    unit_price: 0,
  });

  const handleAddItem = () => {
    if (!item.description || !item.hsn_sac || item.quantity <= 0 || item.unit_price <= 0) {
      alert('Please fill all item fields');
      return;
    }
    onAdd(item);
    setItem({ description: '', hsn_sac: '', quantity: 1, unit_price: 0 });
  };

  return (
    <div className="border-t border-gray-200 pt-5">
      <p className="text-sm font-medium text-gray-700 mb-3">Add New Item</p>
      <div className="space-y-3">
        <div className="grid md:grid-cols-2 gap-3">
          <input
            placeholder="Description *"
            className="form-input-sm"
            value={item.description}
            onChange={(e) => setItem({...item, description: e.target.value})}
          />
          <input
            placeholder="HSN/SAC Code *"
            maxLength={15}
            className="form-input-sm"
            value={item.hsn_sac}
            onChange={(e) => setItem({...item, hsn_sac: e.target.value})}
          />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <input
            type="number"
            placeholder="Quantity *"
            min="1"
            className="form-input-sm"
            value={item.quantity}
            onChange={(e) => setItem({...item, quantity: parseFloat(e.target.value) || 1})}
          />
          <input
            type="number"
            placeholder="Unit Price *"
            min="0"
            step="0.01"
            className="form-input-sm"
            value={item.unit_price}
            onChange={(e) => setItem({...item, unit_price: parseFloat(e.target.value) || 0})}
          />
          <button
            type="button"
            onClick={handleAddItem}
            className="btn-success py-2 flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
