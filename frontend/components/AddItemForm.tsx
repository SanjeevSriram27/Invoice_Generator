'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import type { InvoiceItem } from '@/types/invoice';

interface AddItemFormProps {
  onAdd: (item: InvoiceItem) => void;
}

export default function AddItemForm({ onAdd }: AddItemFormProps) {
  const [item, setItem] = useState({
    description: '',
    hsn_sac: '',
    quantity: '',
    unit_price: '',
  });

  const handleAddItem = () => {
    const quantity = parseFloat(item.quantity);
    const unit_price = parseFloat(item.unit_price);

    if (!item.description || !item.hsn_sac || !quantity || quantity <= 0 || !unit_price || unit_price <= 0) {
      toast.error('Please fill all item fields');
      return;
    }

    onAdd({
      description: item.description,
      hsn_sac: item.hsn_sac,
      quantity,
      unit_price,
    });
    setItem({ description: '', hsn_sac: '', quantity: '', unit_price: '' });
    toast.success('Item added successfully!');
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 pt-5">
      <p className="label-text mb-3">Add New Item</p>
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
            onChange={(e) => setItem({...item, quantity: e.target.value})}
          />
          <input
            type="number"
            placeholder="Unit Price *"
            min="0"
            step="0.01"
            className="form-input-sm"
            value={item.unit_price}
            onChange={(e) => setItem({...item, unit_price: e.target.value})}
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
